#!/usr/bin/env python3
"""
Update Vector Database with Comprehensive Investment Instrument Data
This script exports detailed instrument data from the investment database
and creates a comprehensive vector database for better LLM context.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from investment_database import InvestmentDatabase

def export_instrument_data():
    """Export comprehensive instrument data for vector database"""
    print("🔄 Exporting instrument data from investment database...")
    
    db = InvestmentDatabase()
    
    # Get all instruments
    instruments_df = db.get_all_instruments()
    print(f"📊 Found {len(instruments_df)} instruments")
    
    # Get performance metrics
    performance_df = db.get_performance_metrics()
    print(f"📈 Found performance data for {len(performance_df)} instruments")
    
    # Merge instruments with performance data
    merged_df = instruments_df.merge(performance_df, on='symbol', how='left')
    
    documents = []
    ids = []
    
    print("🔄 Creating vector documents...")
    
    for index, row in merged_df.iterrows():
        # Create comprehensive document content for each instrument
        content_parts = []
        
        # Basic instrument information
        content_parts.append(f"Instrument: {row['name']} ({row['symbol']})")
        content_parts.append(f"Category: {row['category']}")
        content_parts.append(f"Market: {row['market']}")
        content_parts.append(f"Currency: {row['currency']}")
        content_parts.append(f"Risk Level: {row['risk_level']}/10")
        content_parts.append(f"Minimum Investment: {row['currency']} {row['min_investment']:,.0f}")
        
        # Financial metrics
        if pd.notna(row.get('expense_ratio')):
            content_parts.append(f"Expense Ratio: {row['expense_ratio']:.2%}")
        if pd.notna(row.get('dividend_yield')):
            content_parts.append(f"Dividend Yield: {row['dividend_yield']:.2%}")
        
        # Sharia compliance
        compliance = "Sharia-compliant" if row['is_sharia_compliant'] else "Not Sharia-compliant"
        content_parts.append(f"Compliance: {compliance}")
        
        # Performance metrics (if available)
        if pd.notna(row.get('one_year_return')):
            content_parts.append(f"1-Year Return: {row['one_year_return']:.2%}")
        if pd.notna(row.get('three_year_return')):
            content_parts.append(f"3-Year Return: {row['three_year_return']:.2%}")
        if pd.notna(row.get('five_year_return')):
            content_parts.append(f"5-Year Return: {row['five_year_return']:.2%}")
        if pd.notna(row.get('volatility')):
            content_parts.append(f"Volatility: {row['volatility']:.2%}")
        if pd.notna(row.get('sharpe_ratio')):
            content_parts.append(f"Sharpe Ratio: {row['sharpe_ratio']:.2f}")
        if pd.notna(row.get('max_drawdown')):
            content_parts.append(f"Max Drawdown: {row['max_drawdown']:.2%}")
        
        # Description
        if pd.notna(row.get('description')):
            content_parts.append(f"Description: {row['description']}")
        
        # Investment characteristics based on category
        if 'Bond' in row['category'] or 'Sukuk' in row['category']:
            content_parts.append("Investment Type: Fixed Income, Stable Returns, Lower Risk")
        elif 'Stock' in row['category'] or 'Equity' in row['category']:
            content_parts.append("Investment Type: Equity, Growth Potential, Higher Risk")
        elif 'ETF' in row['category']:
            content_parts.append("Investment Type: Diversified Fund, Moderate Risk, Broad Exposure")
        elif 'REIT' in row['category']:
            content_parts.append("Investment Type: Real Estate, Income Generation, Moderate Risk")
        
        # Create document
        document_content = "\n".join(content_parts)
        
        document = Document(
            page_content=document_content,
            metadata={
                "symbol": row['symbol'],
                "name": row['name'],
                "category": row['category'],
                "market": row['market'],
                "risk_level": row['risk_level'],
                "is_sharia_compliant": row['is_sharia_compliant'],
                "type": "instrument_profile"
            },
            id=f"instrument_{row['symbol']}"
        )
        
        documents.append(document)
        ids.append(f"instrument_{row['symbol']}")
    
    # Add historical market data documents
    print("🔄 Adding historical market analysis documents...")
    
    # Get recent historical data for key instruments
    key_symbols = ['ADCB', 'EMAAR', 'ALDAR', 'FAB', 'ADNOC']  # Key UAE instruments
    
    for symbol in key_symbols:
        try:
            hist_data = db.get_historical_data(symbol)
            if not hist_data.empty:
                # Create market analysis document
                recent_data = hist_data.tail(30)  # Last 30 days
                
                avg_price = recent_data['close_price'].mean()
                price_volatility = recent_data['close_price'].std() / avg_price
                avg_volume = recent_data['volume'].mean()
                
                price_trend = "increasing" if recent_data['close_price'].iloc[-1] > recent_data['close_price'].iloc[0] else "decreasing"
                
                analysis_content = f"""
Market Analysis for {symbol}:
Recent 30-day average price: {avg_price:.2f}
Price volatility: {price_volatility:.2%}
Average trading volume: {avg_volume:,.0f}
Recent price trend: {price_trend}
Market activity: {"High" if avg_volume > 1000000 else "Moderate" if avg_volume > 100000 else "Low"}
Investment consideration: Suitable for {"conservative" if price_volatility < 0.02 else "moderate" if price_volatility < 0.05 else "aggressive"} investors
"""
                
                document = Document(
                    page_content=analysis_content,
                    metadata={
                        "symbol": symbol,
                        "type": "market_analysis",
                        "timeframe": "30_days"
                    },
                    id=f"analysis_{symbol}"
                )
                
                documents.append(document)
                ids.append(f"analysis_{symbol}")
                
        except Exception as e:
            print(f"⚠️  Could not process historical data for {symbol}: {e}")
    
    db.close()
    
    print(f"✅ Created {len(documents)} vector documents")
    return documents, ids

def update_vector_database():
    """Update the vector database with comprehensive instrument data"""
    print("🚀 Starting vector database update...")
    
    # Get script directory for consistent paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    vector_db_location = os.path.join(script_dir, "enhanced_investment_vector_db")
    
    # Remove existing vector database
    if os.path.exists(vector_db_location):
        import shutil
        shutil.rmtree(vector_db_location)
        print("🗑️  Removed existing vector database")
    
    # Create new directory
    os.makedirs(vector_db_location, exist_ok=True)
    
    # Initialize embeddings
    print("🔄 Initializing embeddings model...")
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    
    # Export instrument data
    documents, ids = export_instrument_data()
    
    # Create vector store
    print("🔄 Creating vector store...")
    vector_store = Chroma(
        collection_name="enhanced_investment_data",
        persist_directory=vector_db_location,
        embedding_function=embeddings
    )
    
    # Add documents in batches to avoid memory issues
    batch_size = 50
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]

        print(f"🔄 Adding batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        vector_store.add_documents(documents=batch_docs, ids=batch_ids)

    # Note: Chroma automatically persists when using persist_directory
    
    print("✅ Vector database updated successfully!")
    print(f"📍 Location: {vector_db_location}")
    print(f"📊 Total documents: {len(documents)}")
    
    return vector_store

def test_vector_database():
    """Test the updated vector database"""
    print("\n🧪 Testing updated vector database...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    vector_db_location = os.path.join(script_dir, "enhanced_investment_vector_db")
    
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    
    vector_store = Chroma(
        collection_name="enhanced_investment_data",
        persist_directory=vector_db_location,
        embedding_function=embeddings
    )
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # Test queries
    test_queries = [
        "UAE banking stocks with good dividend yield",
        "Sharia compliant bonds and sukuk",
        "Low risk fixed income investments",
        "Real estate investment trusts REIT",
        "US technology stocks high growth"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = retriever.invoke(query)
        
        if results:
            print(f"✅ Found {len(results)} relevant results")
            for i, doc in enumerate(results[:2]):  # Show first 2 results
                print(f"  Result {i+1}: {doc.page_content[:100]}...")
        else:
            print("❌ No results found")
    
    print("\n✅ Vector database test completed!")

if __name__ == "__main__":
    print("🏦 Enhanced Investment Vector Database Updater")
    print("=" * 50)
    
    try:
        # Update vector database
        vector_store = update_vector_database()
        
        # Test the database
        test_vector_database()
        
        print("\n🎉 Vector database update completed successfully!")
        print("💡 You can now use the enhanced vector database in your financial planner.")
        
    except Exception as e:
        print(f"❌ Error updating vector database: {e}")
        import traceback
        traceback.print_exc()
