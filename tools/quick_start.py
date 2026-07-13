#!/usr/bin/env python3
"""
Quick Start Script for Drone Simulation Visualizer

This script sets up and runs the arcade visualizer with your simulation.
Simply run: python quick_start.py

You can also specify a map file:
    python quick_start.py my_map.txt
"""

import sys
import os



def main():
    # Get map file from command line or use default
    if len(sys.argv) > 1:
        map_file = sys.argv[1]
    else:
        # Default to the impossible dream
        map_file = "01_the_impossible_dream.txt"
    
    # Verify file exists
    if not os.path.exists(map_file):
        print(f"❌ Error: Map file '{map_file}' not found!")
        print(f"\n📁 Available files in current directory:")
        txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
        if txt_files:
            for f in txt_files:
                print(f"   - {f}")
        else:
            print("   No .txt map files found!")
        sys.exit(1)
    
    print(f"\n✅ Loading map: {map_file}")
    print("🚀 Starting visualization...")
    print("\n⌨️  Controls:")
    print("   SPACE     → Play/Pause")
    print("   R         → Reset")
    print("   RIGHT     → Step forward")
    print("   Slider    → Adjust speed")
    print()
    
    try:
        app = DroneVisualizerApp(map_file)
        app.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Ensure all files are in the same directory:")
        print("      - Graph.py, simulation.py, map_parser.py")
        print("      - error_handling.py")
        print("      - Your map file (.txt)")
        print("   2. Install arcade: pip install arcade")
        print("   3. Check map file format is valid")
        sys.exit(1)


if __name__ == "__main__":
    main()
