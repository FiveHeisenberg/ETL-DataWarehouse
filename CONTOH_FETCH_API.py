"""
Contoh script untuk fetch data dari Dispenda API lokal.
Ini menunjukkan cara yang akan digunakan di Airflow DAG nantinya.
"""

import requests
import json
from typing import Dict, Any, List

class DispendeAPIClient:
    """Client untuk mengakses Dispenda API read-only"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_table_data(self, endpoint: str, page: int = 1, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch data dari endpoint tertentu
        
        Args:
            endpoint: Nama endpoint (e.g., 'kategori-pajak', 'wajib-pajak')
            page: Nomor halaman (default 1)
            limit: Jumlah record per halaman (default 100, max 1000)
        
        Returns:
            Dict dengan struktur: {
                'success': bool,
                'data': list,
                'pagination': {...}
            }
        """
        url = f"{self.base_url}/{endpoint}"
        params = {"page": page, "limit": limit}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {endpoint}: {e}")
            return {"success": False, "error": str(e)}
    
    def fetch_all_pages(self, endpoint: str, limit: int = 100) -> List[Dict]:
        """
        Fetch semua data dari endpoint dengan auto-pagination
        
        Args:
            endpoint: Nama endpoint
            limit: Jumlah record per halaman
        
        Returns:
            List berisi semua records dari endpoint
        """
        all_records = []
        page = 1
        
        while True:
            print(f"  Fetching {endpoint} - page {page}...")
            response = self.get_table_data(endpoint, page=page, limit=limit)
            
            if not response.get('success'):
                print(f"  ❌ Error: {response.get('error')}")
                break
            
            records = response.get('data', [])
            all_records.extend(records)
            
            pagination = response.get('pagination', {})
            print(f"    Loaded {len(records)} records (Total: {pagination.get('total')})")
            
            if not pagination.get('has_next', False):
                break
            
            page += 1
        
        return all_records


def main():
    """Contoh penggunaan"""
    
    print("=" * 60)
    print("CONTOH FETCH DATA DARI DISPENDA API")
    print("=" * 60)
    
    # Inisialisasi client
    client = DispendeAPIClient(base_url="http://localhost:8000/api")
    
    # Test 1: Fetch single page
    print("\n[Test 1] Fetch single page - kategori-pajak")
    result = client.get_table_data('kategori-pajak', page=1, limit=5)
    if result.get('success'):
        print(f"✅ Success! Fetched {len(result['data'])} records")
        print(f"   Total available: {result['pagination']['total']}")
        print("\n   Data sample:")
        for record in result['data'][:2]:
            print(f"     {record}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test 2: Fetch all pages from kategori-pajak
    print("\n[Test 2] Fetch all pages - kategori-pajak")
    all_kategori = client.fetch_all_pages('kategori-pajak', limit=5)
    print(f"✅ Total records fetched: {len(all_kategori)}")
    
    # Test 3: Fetch wajib-pajak with larger batch
    print("\n[Test 3] Fetch all pages - wajib-pajak (large batch)")
    all_wajib = client.fetch_all_pages('wajib-pajak', limit=500)
    print(f"✅ Total records fetched: {len(all_wajib)}")
    
    # Test 4: Test all endpoints with single page
    print("\n[Test 4] Quick test all 6 endpoints")
    endpoints = [
        'kategori-pajak',
        'metode-bayar',
        'wajib-pajak',
        'objek-pajak',
        'tagihan',
        'pembayaran',
    ]
    
    for endpoint in endpoints:
        result = client.get_table_data(endpoint, page=1, limit=1)
        if result.get('success'):
            total = result['pagination']['total']
            print(f"✅ {endpoint:20} → {total:5} total records")
        else:
            print(f"❌ {endpoint:20} → Error: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    main()
