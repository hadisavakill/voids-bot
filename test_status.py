import os, importlib.util, shutil

CHECKS = {
    "Python 3.x": shutil.which("python") is not None,
    "pip": shutil.which("pip") is not None,
    "sentinelhub": importlib.util.find_spec("sentinelhub") is not None,
    "rasterio": importlib.util.find_spec("rasterio") is not None,
    "numpy": importlib.util.find_spec("numpy") is not None,
    "dotenv": importlib.util.find_spec("dotenv") is not None,
    "fpdf": importlib.util.find_spec("fpdf") is not None,
    "simplekml": importlib.util.find_spec("simplekml") is not None,
    "outputs/png folder": os.path.exists("outputs/png"),
    "outputs/geotiff folder": os.path.exists("outputs/geotiff"),
    "subsurface_analyze.py": os.path.exists("subsurface_analyze.py"),
    ".env file": os.path.exists(".env"),
}

print("==== Project Setup Status ====")
for name, ok in CHECKS.items():
    mark = "[OK]" if ok else "[MISSING]"
    print(f"{mark} {name}")

# Show recommendations
missing = [k for k, v in CHECKS.items() if not v]
if missing:
    print("\n--- Recommendations ---")
    for item in missing:
        if item == "sentinelhub":
            print("-> pip install sentinelhub")
        elif item == "rasterio":
            print("-> pip install rasterio")
        elif item == "numpy":
            print("-> pip install numpy")
        elif item == "dotenv":
            print("-> pip install python-dotenv")
        elif item == "fpdf":
            print("-> pip install fpdf")
        elif item == "simplekml":
            print("-> pip install simplekml")
        elif item == "outputs/png folder":
            print("-> mkdir outputs/png")
        elif item == "outputs/geotiff folder":
            print("-> mkdir outputs/geotiff")
        elif item == ".env file":
            print("-> Create your .env file with Sentinel Hub keys")
        elif item == "subsurface_analyze.py":
            print("-> Make sure your main Python file exists.")
else:
    print("\nAll checks passed. You're ready to go!")