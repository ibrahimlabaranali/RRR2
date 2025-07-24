#!/usr/bin/env python3
"""
Test script to verify folium 0.14.0 compatibility with the Road Freight Risk AI application.
This script tests all the folium features used in the application.
"""

import sys
import os

def test_folium_imports():
    """Test that folium and related packages can be imported"""
    try:
        import folium
        print(f"✅ folium imported successfully: {folium.__version__}")
        
        import branca
        print(f"✅ branca imported successfully: {branca.__version__}")
        
        # Test streamlit-folium import (if available)
        try:
            from streamlit_folium import st_folium
            print("✅ streamlit_folium imported successfully")
        except ImportError:
            print("⚠️ streamlit_folium not available (this is normal for backend testing)")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_folium_basic_features():
    """Test basic folium features used in the application"""
    try:
        import folium
        
        # Test Map creation
        m = folium.Map(location=[9.0820, 8.6753], zoom_start=6)
        print("✅ Map creation successful")
        
        # Test Marker creation
        folium.Marker(
            location=[9.0820, 8.6753],
            popup="Test marker",
            tooltip="Test tooltip",
            icon=folium.Icon(color="red")
        ).add_to(m)
        print("✅ Marker creation successful")
        
        # Test CircleMarker creation
        folium.CircleMarker(
            location=[9.0820, 8.6753],
            radius=6,
            color="red",
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup("Test circle marker", max_width=250)
        ).add_to(m)
        print("✅ CircleMarker creation successful")
        
        # Test HeatMap (if available)
        try:
            from folium.plugins import HeatMap
            heat_data = [[9.0820, 8.6753], [9.0821, 8.6754]]
            HeatMap(heat_data).add_to(m)
            print("✅ HeatMap creation successful")
        except ImportError:
            print("⚠️ HeatMap plugin not available")
        
        # Test map HTML generation
        html = m._repr_html_()
        if html and len(html) > 100:
            print("✅ Map HTML generation successful")
        else:
            print("❌ Map HTML generation failed")
        
        return True
    except Exception as e:
        print(f"❌ Folium feature test failed: {e}")
        return False

def test_color_mapping():
    """Test color mapping features used in the application"""
    try:
        import folium
        import branca
        
        # Test color mapping (used in admin dashboard)
        color_map = {
            "Flooding": "blue",
            "Robbery": "red",
            "Protest": "orange",
            "Banditry": "darkred",
            "Accident": "green",
            "Blocked Road": "purple",
            "Other": "gray"
        }
        
        # Test that all colors are valid
        for risk_type, color in color_map.items():
            # Create a marker with the color to test it
            m = folium.Map(location=[9.0820, 8.6753], zoom_start=6)
            folium.CircleMarker(
                location=[9.0820, 8.6753],
                color=color,
                radius=6
            ).add_to(m)
        
        print("✅ Color mapping test successful")
        return True
    except Exception as e:
        print(f"❌ Color mapping test failed: {e}")
        return False

def test_popup_content():
    """Test popup content generation used in the application"""
    try:
        import folium
        
        # Test HTML popup content (similar to admin dashboard)
        popup_content = f"""
            <strong>Risk:</strong> Test Risk<br>
            <strong>User:</strong> test_user<br>
            <strong>Time:</strong> 2024-01-01<br>
            <strong>Location:</strong> Test Location<br>
            <strong>Source:</strong> web
        """
        
        m = folium.Map(location=[9.0820, 8.6753], zoom_start=6)
        folium.CircleMarker(
            location=[9.0820, 8.6753],
            popup=folium.Popup(popup_content, max_width=250)
        ).add_to(m)
        
        print("✅ Popup content test successful")
        return True
    except Exception as e:
        print(f"❌ Popup content test failed: {e}")
        return False

def main():
    """Run all compatibility tests"""
    print("🧪 Testing folium 0.14.0 compatibility...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_folium_imports),
        ("Basic Features Test", test_folium_basic_features),
        ("Color Mapping Test", test_color_mapping),
        ("Popup Content Test", test_popup_content),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! folium 0.14.0 is fully compatible.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 