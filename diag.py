from mplsoccer import Pitch
import inspect
print("Arguments for Pitch.__init__:")
print(inspect.signature(Pitch.__init__))
print("\nArguments for Pitch.draw:")
print(inspect.signature(Pitch.draw))
