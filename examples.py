from core import AudioType

# Configuration
my_audio = AudioType("Audios/Lost soul down.wav")
silent_audio = AudioType(length=5)

print(my_audio.array) # Amplitude array
print(my_audio.sr) # sample rate
print(my_audio.length) # Length in seconds
my_audio.volume = 0.9
my_audio = my_audio.mono()
my_audio = my_audio.stereo()
print(my_audio.channels) # 1 if mono, 2 if stereo
my_audio = my_audio.trim(5000, 67000)
my_audio = my_audio.trim(None, 120000)
my_audio.copy()
my_audio.open("audio2.wav") # Opens and REPLACES a new audio file for this obj
my_audio.save("new_audio.wav")



a = my_audio.copy()
b = AudioType()

# Effects:
a = a.fx.stereo_effect()
a = a.fx.speed()
a = a.fx.sample_rate(44100)
a = a.fx.merge(b)
a = a.fx.tremolo()
a = a.fx.reverse()
a = a.fx.noise()
a = a.fx.fade_in()
a = a.fx.fade_out()
a = a.fx.pitch()
a = a.fx.stereo_mixer()
a = a.fx.exponential_distortion()
a = a.fx.echo()
a = a.fx.reverb()
a = a.fx.bass_booster()
a = a.fx.microphone()
a = a.fx.low_pass()
a = a.fx.high_pass()

# Chaining:
a = a.fx.reverb().fx.bass_booster().fx.echo()

# Method 2:
from core import AudioEffects
new_a = AudioEffects(a).high_pass(500)



a = AudioType(length=30, sr = 44100)
a = a.generate.frequency(rate_hz=1000)
b = a.generate.noise()
result = a.fx.merge(b)

# Method 2:
from core import GenerateAudio
noise = GenerateAudio(a).noise()



a = a.eq.three_band_eq(1.2, 1, 0.8)
a = a.eq.nine_band_eq(1.2, 1.2, 1.1, 1, 1, 1, 1, 0.8, 0.7)
a = a.eq.custom_eq(start_freq=100, end_freq=600, in_range_multiplier=1.3, out_range_multiplier=0.5)

# Use interactive GUI (simple tkinter window). Uses the nine_band_eq function:
a = a.eq.gui()  
# A tkinter window will pop up with 9 sliders. 
# Effect will be applied automatically after gui is closed.

# See also:
from core import Equalizer
eqed_a = Equalizer(a).custom_eq(100, 200)



a.visuals.waveform() # plt window will pop up
a.visuals.spectrums() # plt window will pop up

# Show updates live:
a = a.fx.high_pass(500)
a.visuals.spectrums()

