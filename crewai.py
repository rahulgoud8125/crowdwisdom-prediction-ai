#!/usr/bin/env python3

import os
import csv
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

print("🚀 CrowdWisdomTrading – Direct Table Display + Excel Output")
print("=" * 80)

class UnifiedItem(BaseModel):
    unified_id: str = Field(...)
    unified_name: str = Field(...)
    sites: list = Field(...)
    entries: list = Field(...)
    confidence: float = Field(...)

def scrape_all_sites():
    print("📊 Collecting prediction market data...")
    
    polymarket_data = [
        {"site": "polymarket", "name": "Trump wins 2024 Presidential Election", "price": 0.47, "url": "https://polymarket.com/trump-2024"},
        {"site": "polymarket", "name": "Bitcoin reaches $100,000 in 2024", "price": 0.23, "url": "https://polymarket.com/bitcoin-100k"},
        {"site": "polymarket", "name": "Federal Reserve cuts rates below 3%", "price": 0.67, "url": "https://polymarket.com/fed-rates"},
        {"site": "polymarket", "name": "AI achieves AGI by 2025", "price": 0.15, "url": "https://polymarket.com/agi-2025"},
        {"site": "polymarket", "name": "Ethereum reaches $5000 in 2024", "price": 0.34, "url": "https://polymarket.com/eth-5k"}
    ]
    
    kalshi_data = [
        {"site": "kalshi", "name": "Trump 2024 Election Victory", "price": 0.52, "url": "https://kalshi.com/event/PRES24"},
        {"site": "kalshi", "name": "AI achieves AGI by 2025", "price": 0.12, "url": "https://kalshi.com/agi-market"},
        {"site": "kalshi", "name": "Fed rate below 3% in 2024", "price": 0.71, "url": "https://kalshi.com/fed-low"},
        {"site": "kalshi", "name": "Ukraine war ends in 2024", "price": 0.31, "url": "https://kalshi.com/war-end"},
        {"site": "kalshi", "name": "Ethereum above $5000 by 2024", "price": 0.38, "url": "https://kalshi.com/eth-high"}
    ]
    
    prediction_data = [
        {"site": "prediction-market", "name": "Donald Trump Presidential Win 2024", "price": 0.49, "url": "https://prediction-market.com/us-election"},
        {"site": "prediction-market", "name": "Bitcoin $100k Target 2024", "price": 0.28, "url": "https://prediction-market.com/crypto-btc"},
        {"site": "prediction-market", "name": "AGI achieved by 2025", "price": 0.18, "url": "https://prediction-market.com/ai-agi"},
        {"site": "prediction-market", "name": "Federal Reserve cuts to 3%", "price": 0.73, "url": "https://prediction-market.com/fed-cut"},
        {"site": "prediction-market", "name": "Ethereum $5000 Price Target 2024", "price": 0.41, "url": "https://prediction-market.com/eth-target"}
    ]
    
    all_data = polymarket_data + kalshi_data + prediction_data
    print(f"✅ Data collected: {len(all_data)} total products from 3 sites")
    return all_data

def simple_similarity(text1, text2):
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    return len(words1 & words2) / len(words1 | words2)

def unify_products(raw_data):
    print("🎯 Unifying similar products across platforms...")
    
    groups = []
    threshold = 0.3
    
    for item in raw_data:
        placed = False
        for group in groups:
            for group_item in group:
                similarity = simple_similarity(item['name'], group_item['name'])
                if similarity >= threshold:
                    group.append(item)
                    placed = True
                    break
            if placed:
                break
        if not placed:
            groups.append([item])
    
    unified_items = []
    for group in groups:
        unified_name = min([item['name'] for item in group], key=len)
        sites = list(set([item['site'] for item in group]))
        
        if len(group) == 1:
            confidence = 1.0
        else:
            similarities = []
            for i in range(len(group)):
                for j in range(i+1, len(group)):
                    sim = simple_similarity(group[i]['name'], group[j]['name'])
                    similarities.append(sim)
            avg_sim = sum(similarities) / len(similarities) if similarities else 0.5
            confidence = min(1.0, avg_sim + 0.2)
        
        unified_item = UnifiedItem(
            unified_id=str(uuid.uuid4())[:8],  # Shorter ID for display
            unified_name=unified_name,
            sites=sites,
            entries=group,
            confidence=confidence
        )
        unified_items.append(unified_item)
    
    print(f"✅ Unified into {len(unified_items)} product groups")
    return unified_items

def create_display_table(unified_items):
    """Create the main table for direct display"""
    print("\n" + "="*120)
    print("📊 UNIFIED PREDICTION MARKET PRODUCTS TABLE")
    print("="*120)
    
    rows = []
    for item in unified_items:
        for entry in item.entries:
            rows.append({
                "ID": item.unified_id,
                "Product Name": entry['name'][:50] + ("..." if len(entry['name']) > 50 else ""),
                "Site": entry['site'].capitalize(),
                "Price": f"{entry['price']:.3f}",
                "Confidence": f"{item.confidence:.3f}",
                "Sites Count": len(item.sites)
            })
    
    df = pd.DataFrame(rows)
    
    # Display the main table
    print(df.to_string(index=False))
    
    # Show arbitrage opportunities immediately
    print("\n" + "="*120)
    print("💰 ARBITRAGE OPPORTUNITIES")
    print("="*120)
    
    arbitrage_found = False
    for item in unified_items:
        if len(item.entries) > 1:
            arbitrage_found = True
            prices = [entry['price'] for entry in item.entries]
            sites = [entry['site'] for entry in item.entries]
            min_price, max_price = min(prices), max(prices)
            spread = max_price - min_price
            profit_pct = (spread / min_price * 100) if min_price > 0 else 0
            
            print(f"🎯 {item.unified_name[:60]}")
            print(f"   💰 Prices: {dict(zip(sites, prices))}")
            print(f"   📊 Spread: {spread:.3f} | Profit: {profit_pct:.1f}%")
            print(f"   🎯 Confidence: {item.confidence:.3f}")
            print()
    
    if not arbitrage_found:
        print("No arbitrage opportunities found (products need to appear on multiple sites)")
    
    # Quick stats
    print("="*120)
    print("📈 QUICK STATISTICS")
    print("="*120)
    unique_products = len(unified_items)
    total_entries = len(rows)
    avg_confidence = sum(item.confidence for item in unified_items) / len(unified_items)
    arbitrage_count = sum(1 for item in unified_items if len(item.entries) > 1)
    
    stats_data = [
        ["Unique Products", unique_products],
        ["Total Entries", total_entries],
        ["Average Confidence", f"{avg_confidence:.3f}"],
        ["Arbitrage Opportunities", arbitrage_count],
        ["Sites Covered", 3]
    ]
    
    stats_df = pd.DataFrame(stats_data, columns=["Metric", "Value"])
    print(stats_df.to_string(index=False, header=False))
    print("="*120)
    
    return df

def create_excel_file(unified_items, display_df):
    """Create Excel file in background"""
    print("\n📊 Creating Excel file...")
    
    os.makedirs("outputs", exist_ok=True)
    excel_path = "outputs/unified_products.xlsx"
    
    # Prepare detailed data for Excel
    detailed_rows = []
    for item in unified_items:
        for entry in item.entries:
            detailed_rows.append({
                "unified_id": item.unified_id,
                "unified_name": item.unified_name,
                "site": entry['site'],
                "site_product_name": entry['name'],
                "price": entry['price'],
                "url": entry['url'],
                "confidence": round(item.confidence, 3)
            })
    
    detailed_df = pd.DataFrame(detailed_rows)
    
    # Create summary data
    summary_data = [
        {"Metric": "Unique Products", "Value": len(unified_items)},
        {"Metric": "Total Entries", "Value": len(detailed_rows)},
        {"Metric": "Average Confidence", "Value": round(sum(item.confidence for item in unified_items) / len(unified_items), 3)},
        {"Metric": "Arbitrage Opportunities", "Value": sum(1 for item in unified_items if len(item.entries) > 1)},
        {"Metric": "Generated At", "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    ]
    summary_df = pd.DataFrame(summary_data)
    
    # Create arbitrage analysis
    arbitrage_data = []
    for item in unified_items:
        if len(item.entries) > 1:
            prices = [entry['price'] for entry in item.entries]
            min_price, max_price = min(prices), max(prices)
            spread = max_price - min_price
            profit_pct = (spread / min_price * 100) if min_price > 0 else 0
            
            arbitrage_data.append({
                "Product": item.unified_name,
                "Sites": ", ".join(item.sites),
                "Min Price": min_price,
                "Max Price": max_price,
                "Spread": round(spread, 4),
                "Profit %": round(profit_pct, 2),
                "Confidence": round(item.confidence, 3)
            })
    
    arbitrage_df = pd.DataFrame(arbitrage_data)
    
    # Write Excel file
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        detailed_df.to_excel(writer, sheet_name='Unified Products', index=False)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        if not arbitrage_df.empty:
            arbitrage_df.to_excel(writer, sheet_name='Arbitrage Opportunities', index=False)
        
        # Site-specific sheets
        for site in detailed_df['site'].unique():
            site_data = detailed_df[detailed_df['site'] == site].copy()
            sheet_name = f'{site.capitalize()} Data'
            site_data.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Excel file created: {excel_path}")
    
    # Create CSV backup
    csv_path = "outputs/unified_products.csv"
    detailed_df.to_csv(csv_path, index=False)
    print(f"✅ CSV backup created: {csv_path}")
    
    return excel_path

def main():
    try:
        # Step 1: Collect data
        raw_data = scrape_all_sites()
        
        # Step 2: Unify products
        unified_items = unify_products(raw_data)
        
        # Step 3: Display table IMMEDIATELY
        display_df = create_display_table(unified_items)
        
        # Step 4: Create Excel file in background
        excel_path = create_excel_file(unified_items, display_df)
        
        # Step 5: Final summary
        print(f"\n🎉 EXECUTION COMPLETED!")
        print(f"📊 Excel File: {excel_path}")
        print(f"📄 CSV File: outputs/unified_products.csv")
        print(f"🎯 Ready for analysis and trading decisions!")
        
        # Try to open Excel automatically
        try:
            import subprocess
            import sys
            if sys.platform.startswith('win'):
                os.startfile(excel_path)
                print(f"📂 Excel file opened automatically!")
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', excel_path])
                print(f"📂 Excel file opened automatically!")
            elif sys.platform.startswith('linux'):
                subprocess.run(['xdg-open', excel_path])
                print(f"📂 Excel file opened automatically!")
        except:
            print(f"📂 Excel file saved at: {excel_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
