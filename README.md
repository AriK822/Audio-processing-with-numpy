# Audio processing in numpy

## About:
A solo dev educational practice on audio processing with raw audio data (using numpy)

## Clone the repo
To clone the repo, run:
```Bash
git clone https://github.com/AriK822/Audio-processing-with-numpy.git
```

## Requirements:
- soundfile (python library)
- numpy (python library)
- matplotlib (python library)

Run:
```bash
pip install soundfile numpy matplotlib
```

## Quick start
```python
## Quick Start
from core import AudioType

# Load audio
audio = AudioType("my_song.wav")

# Apply effects
processed = (audio
    .fx.reverb(room_size=0.5)
    .fx.bass_booster(boost_db=6)
    .fx.echo(delay_ms=250)
)

# Visualize
processed.visuals.waveform()
processed.visuals.spectrums()

# Save
processed.save("processed_song.wav")
```

# Examples:
After cloning the repo, start coding in examples.py or create your own python file.


Create an AudioType obj. Name an existing wav file's path to open it, if no path is passed, a silent audio using length and sr (sample_rate) parameters will be created:

```Python
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
```

## Effects:
Every operation returns an AudioType obj.

Examples:
```Python
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
```

## Generating:
Note that using .generate creates a new AudioType obj that overwrites the data. To blend with original, use .fx.merge().

Examples:
```Python
a = AudioType(length=30, sr = 44100)
a = a.generate.frequency(rate_hz=1000)
a = a.generate.noise()
a = a.generate.morse_code("Morse code!")

# Method 2:
from core import GenerateAudio
noise = GenerateAudio(a).noise()
```

## Equalizer:
Use the equalizer tab to modify and resample a frequesncy band.

Note: This class is power by numpy's Fast Fourier Transform (FFT) function.

Examples:
```Python
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
```

### Preview:
The .eq.gui() method opens a GUI window like following:
![Equalizer GUI](/previews/prev3.png)


## Visuals:
View waveform and spectrums made from AudioType object.
Note: Requires matplotlib!

Examples:
```Python
a.visuals.waveform() # plt window will pop up
a.visuals.spectrums() # plt window will pop up

# Show updates live:
a = a.fx.high_pass(500)
a.visuals.spectrums()
```

### Previews:
Waveform (amplitude / time):
![Waveform](/previews/prev1.png)

Spectrums (amplitude / frequency):
![Spectrums](/previews/prev2.png)





## Abstract Reference Table (AI made):

### AudioType Core Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `AudioType()` | `path: str\|None=None`, `length=10`, `sr=44100` | Load file or create silent audio |
| `.open()` | `path: str` | Load new audio file |
| `.save()` | `path: str="output.wav"` | Save to file |
| `.copy()` | - | Return deep copy |
| `.trim()` | `start_ms:int\|float\|None = None`, `end_ms:int\|float\|None = None` | Trim (cut) the audio file |
| `.mono()` | - | Convert to mono (average channels) |
| `.stereo()` | - | Convert to stereo (duplicate mono) |
| `.channels` | - | channel count (mono = 1, stereo = 2) |
| `.volume` | property getter/setter | Get or set volume multiplier |
| `.length` | - | Audio length in seconds |

### Effects (via `.fx`)

| Method | Parameters | Default | Description |
|--------|------------|---------|-------------|
| `.stereo_effect()` | `speed_sec`, `decay` | `1, 1` | Stereo panning rotation |
| `.speed()` | `new_speed` | `1` | Change playback speed |
| `.sample_rate()` | `new_sr`, `same_length` | `, True` | Change sample rate |
| `.merge()` | `audio2`, `volume1`, `volume2`, `delay1_ms`, `delay2_ms` | `, 0.5, 0.5, 0, 0` | Mix with another audio |
| `.tremolo()` | `rate_hz` | `10` | Volume modulation |
| `.reverse()` | - | - | Reverse audio |
| `.noise()` | `intensity`, `max_offset` | `0.1, 10` | Add glitch noise |
| `.fade_in()` | `duration_sec` | `3` | Fade in from silence |
| `.fade_out()` | `duration_sec` | `3` | Fade out to silence |
| `.pitch()` | `shift`, `chunk_size` | `1, 3072` | Pitch shift (1=no change) |
| `.stereo_mixer()` | `left_channel`, `right_channel` | `0.5, 0.5` | Adjust channel volumes |
| `.exponential_distortion()` | `amount` | `0.5` | Waveshaping distortion |
| `.echo()` | `delay_ms`, `decay` | `300, 0.5` | Single echo |
| `.reverb()` | `delay_ms`, `decay`, `n`, `decay_exp` | `50, 0.2, 15, 5` | Multi-echo reverb |
| `.bass_booster()` | `multiplier` | `1.2` | Boost bass frequencies |
| `.microphone()` | `multiplier` | `1.3` | Telephone/mic effect |
| `.low_pass()` | `freq` | `500` | Cut frequencies above |
| `.high_pass()` | `freq` | `500` | Cut frequencies below |

### Generation (via `.generate`)

| Method | Parameters | Default | Description |
|--------|------------|---------|-------------|
| `.frequency()` | `rate_hz` | `1000` | Generate sine wave |
| `.noise()` | - | - | Generate white noise |
| `.morse_code()` | `text:str, unit_ms:int, frequency, print_code, keep_length` | `, 100, 800, True, False` | Generate morse code |

### Equalizer (via `.eq`)

| Method | Parameters | Description |
|--------|------------|-------------|
| `.custom_eq()` | `start_freq`, `end_freq`, `in_range_multiplier=1.2`, `out_range_multiplier=0.8` | Custom frequency band EQ |
| `.three_band_eq()` | `_0_500=1.`, `_500_2k=1.`, `_2k_16k=1.` | Simple 3-band EQ |
| `.nine_band_eq()` | `_0_63=1.`, `_63_125=1.`, `_125_250=1.`, `_250_500=1.`, `_500_1k=1.`, `_1k_2k=1.`, `_2k_4k=1.`, `_4k_8k=1.`, `_8k_16k=1.` | Graphic 9-band EQ |
| `.gui()` | - | Open tkinter EQ window |

### Visuals (via `.visuals`)

| Method | Parameters | Default | Description |
|--------|------------|---------|-------------|
| `.waveform()` | `samples` | `10000` | Plot waveform |
| `.spectrums()` | - | - | Plot frequency spectrum |



## Contributing
This is an educational project. Feel free to:
- Fork and experiment
- Submit issues for bugs
- Add new effects via pull requests

### Adding a New Effect
```python
def my_effect(self, param=1.0) -> AudioType:
    result = self._audio_obj.copy()
    # Your effect logic here
    result.array = processed_audio
    return result