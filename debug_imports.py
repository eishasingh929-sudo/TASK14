import sys
import os
import traceback

# Add project root to sys.path
root = r"c:\Users\Yass0\OneDrive\Desktop\TASK14"
if root not in sys.path:
    sys.path.insert(0, root)

print("Starting debug import...")
try:
    print("Importing uniguru.core.rules.base...")
    from uniguru.core.rules.base import RuleAction
    print("Success.")
    
    print("Importing uniguru.enforcement.safety...")
    from uniguru.enforcement.safety import SafetyRule
    print("Success.")
    
    print("Importing uniguru.core.rules...")
    import uniguru.core.rules
    print("Success.")
    print("uniguru.core.rules attributes:", dir(uniguru.core.rules))
    
    from uniguru.core.rules import SafetyRule
    print("Imported SafetyRule from uniguru.core.rules success.")

except Exception:
    traceback.print_exc()
