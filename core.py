import soundfile as sf
import numpy as np



class AudioType:
    def __init__(self, path:str|None=None, length = 10, sr = 44100):
        "Import from audio file or create an empty amplitude array."
        if not path:
            self.array = np.zeros((length * sr, 2))
            self.sr = sr
        else:
            self.array, self.sr = sf.read(path)

        self._volume = 1
        self.fx = AudioEffects(self)
        self.generate = GenerateAudio(self)
        self.eq = Equalizer(self)
        self.visuals = Visuals(self)

    
    @property
    def volume(self):
        return self._volume
    

    @volume.setter
    def volume(self, value):
        self._volume = value


    @property
    def length(self):
        return round(len(self.array) / self.sr, 3)


    def open(self, path:str):
        self.array, self.sr = sf.read(path)


    def save(self, path:str = "output.wav"):
        sf.write(path, self.array * self.volume, self.sr)

    
    def copy(self) -> "AudioType":
        temp = AudioType()
        temp.array = self.array.copy()
        temp.sr = self.sr
        temp.volume = self.volume
        return temp
    

    def mono(self) -> "AudioType":
        if len(self.array.shape) == 1: return self.copy()

        result = self.copy()
        result.array = np.mean(result.array, axis=1)
        return result


    def stereo(self) -> "AudioType":
        if len(self.array.shape) == 2: return self.copy()

        result = self.copy()
        result.array = np.column_stack([result.array, result.array])
        return result
    

    @property
    def channels(self):
        shape = self.array.shape
        if len(shape) == 1: return 1
        if shape[1] == 1: return 1
        if shape[1] == 2: return 2
        return None
    

    def trim(self, start_ms:int|float|None = None, end_ms:int|float|None = None) -> "AudioType":
        result = self.copy()
        if not start_ms and not end_ms:pass
        elif not start_ms and end_ms:
            e_index = int(end_ms / 1000 * self.sr)
            result.array = result.array[:e_index]
        elif not end_ms and start_ms:
            s_index = int(start_ms / 1000 * self.sr)
            result.array = result.array[s_index:]
        elif start_ms and end_ms:
            s_index = int(start_ms / 1000 * self.sr)
            e_index = int(end_ms / 1000 * self.sr)
            result.array = result.array[s_index:e_index]
        return result
    



class AudioEffects:
    def __init__(self, audio_obj:AudioType) -> None:
        self._audio_obj = audio_obj


    def stereo_effect(self, speed_sec = 1, decay = 1) -> AudioType:
        result = self._audio_obj.copy()
        t = np.arange(len(result.array))
        left_volume = np.sin(t * np.pi * 2 / result.sr * speed_sec) * decay
        right_volume = np.cos(t * np.pi * 2 / result.sr * speed_sec) * decay
        result.array[:, 0] *= left_volume
        result.array[:, 1] *= right_volume
        return result


    def speed(self, new_speed:int|float = 1) -> AudioType:
        new_size = round(len(self._audio_obj.array) / new_speed)
        indecies = (np.arange(new_size) * new_speed).astype(int)
        new_arr = self._audio_obj.array[indecies]
        result = self._audio_obj.copy()
        result.array = new_arr
        return result
    

    def sample_rate(self, new_sr:int, same_length = True) -> AudioType:
        result = self._audio_obj.copy()
        result.sr = new_sr

        if same_length:
            result = result.fx.speed(self._audio_obj.sr / new_sr)

        return result

    

    def merge(self, audio2:AudioType, volume1 = 0.5, volume2 = 0.5, delay1_ms=0, delay2_ms=0) -> AudioType:
        array1, sr1 = self._audio_obj.array, self._audio_obj.sr
        array2, sr2 = audio2.array, audio2.sr

        if delay1_ms != 0:
            array1 = np.vstack([np.zeros((int(delay1_ms/1000*sr1), array1.shape[1])), array1])

        if delay2_ms != 0:
            array2 = np.vstack([np.zeros((int(delay2_ms/1000*sr2), array2.shape[1])), array2])

        if sr1 != sr2:
            audio2 = audio2.fx.sample_rate(sr1, True)
            array2, sr2 = audio2.array, audio2.sr

        newarr = np.zeros((len(array1) if len(array1) > len(array2) else len(array2), 2))
        newarr[:len(array1)] += array1 * volume1
        newarr[:len(array2)] += array2 * volume2

        result = self._audio_obj.copy()
        result.array = newarr
        return result
    

    def tremolo(self, rate_hz = 10) -> AudioType:
        result = self._audio_obj.copy()
        t = np.arange(len(result.array))
        result.array[:, 0] *= np.sin(t * np.pi * 2 / result.sr * rate_hz)
        result.array[:, 1] *= np.sin(t * np.pi * 2 / result.sr * rate_hz)
        return result

    
    def reverse(self) -> AudioType:
        result = self._audio_obj.copy()
        result.array = result.array[::-1]
        return result
    

    def noise(self, intensity = 0.1, max_offest = 10) -> AudioType:
        result = self._audio_obj.copy()
        indecies = np.random.choice(len(result.array), int(len(result.array)*intensity), replace=False)
        offsets = np.random.randint(-max_offest, max_offest, len(indecies))
        result.array[indecies]  = result.array[np.clip(indecies + offsets, 0, len(result.array)-1)]
        return result


    def fade_in(self, duration_sec=3) -> AudioType:
        result = self._audio_obj.copy()
        fade = (np.arange(int(duration_sec * result.sr)) / int(duration_sec * result.sr)).reshape(-1, 1)
        result.array[:len(fade)] *= fade
        return result


    def fade_out(self, duration_sec=3) -> AudioType:
        result = self._audio_obj.copy()
        fade = (np.arange(int(duration_sec * result.sr))[::-1] / int(duration_sec * result.sr)).reshape(-1, 1)
        result.array[len(result.array) - len(fade):] *= fade
        return result


    def pitch(self, shift:int|float=1, chunk_size = 3072) -> AudioType:
        result = self._audio_obj.copy()

        if shift > 1:
            result_arr = np.zeros_like(result.array)

            for i in range(0, len(result.array), int(chunk_size / shift)):
                fade_len = 200
                this_chunk = result.array[i:i+chunk_size + int(fade_len * shift)]

                new_size = round(len(this_chunk) / shift)
                indecies = (np.arange(new_size) * shift).astype(int)
                new_arr = this_chunk[indecies]

                fade = (np.arange(fade_len) / (fade_len)).reshape(-1, 1)
                if len(new_arr) >= len(fade) and len(fade) > 0:
                    new_arr[:fade_len] *= fade
                    new_arr[new_size-fade_len:] *= fade[::-1]

                if i + new_size < len(result.array):
                    result_arr[i:i+new_size] += new_arr

            result.array = result_arr

        if shift < 1:
            result_arr = np.zeros_like(result.array)

            for i in range(0, len(result.array), chunk_size):
                this_chunk = result.array[i:i+chunk_size]

                new_size = round(len(this_chunk) / shift)
                indecies = (np.arange(new_size) * shift).astype(int)
                new_arr = this_chunk[indecies]

                fade = (np.arange(new_size - chunk_size) / (new_size - chunk_size)).reshape(-1, 1)
                if len(new_arr) >= len(fade) and len(fade) > 0:
                    new_arr[:new_size-chunk_size] *= fade
                    new_arr[len(new_arr) - (new_size-chunk_size):] *= fade[::-1]

                if i + new_size < len(result.array):
                    result_arr[i:i+new_size] += new_arr

            result.array = result_arr

        return result
    

    def stereo_mixer(self, left_channel = 0.5, right_channel = 0.5) -> AudioType:
        result = self._audio_obj.copy()
        result.array[:, 0] = result.array[:, 0] * left_channel
        result.array[:, 1] = result.array[:, 1] * right_channel
        return result


    def exponential_distortion(self, amount=0.5) -> AudioType:
        result = self._audio_obj.copy()
        
        result.array = np.power(np.abs(result.array), amount)
        result.array *= np.sign(self._audio_obj.array)
        
        result.array = result.array / (np.max(np.abs(result.array)) + 0.01) * 0.9
        
        return result
    

    def echo(self, delay_ms = 300, decay = 0.5):
        result = self._audio_obj.copy()
        delay_samples = int((result.sr * delay_ms) / 1000)
        result.array[delay_samples:] += result.array[:len(result.array)-delay_samples] * decay
        return result
    

    def reverb(self, delay_ms=50, decay=0.2, n=15, decay_exp:int|float = 5):
        def __echo(array, sr, delay_ms:int|float = 300, decay = 0.5):
            delay_samples = int((sr * delay_ms) / 1000)
            array[delay_samples:] += array[:len(array)-delay_samples] * decay
            return array
        
        result = self._audio_obj.copy()
        for i in range(0, delay_ms*n, delay_ms):
            __echo(result.array, result.sr, i, ((1 - i/1000)**decay_exp * decay))

        return result
    

    def bass_booster(self, multiplier = 1.2):
        return self._audio_obj.eq.custom_eq(0, 300, multiplier, 2 - multiplier)
    

    def microphone(self, multiplier = 1.3):
        return self._audio_obj.eq.custom_eq(800, 3000, multiplier, 2 - multiplier)


    def low_pass(self, freq = 500):
        return self._audio_obj.eq.custom_eq(0, freq, 0, 1)
    

    def high_pass(self, freq = 500):
        return self._audio_obj.eq.custom_eq(0, freq, 1, 0)



class GenerateAudio:
    def __init__(self, audio_obj: AudioType):
        self._audio_obj = audio_obj

    
    def frequency(self, rate_hz=1000) -> AudioType:
        result = self._audio_obj.copy()
        wave = np.sin(np.arange(len(result.array)) * np.pi * 2 / result.sr * rate_hz)
        result.array = wave
        return result
    

    def noise(self) -> AudioType:
        result = self._audio_obj.copy()
        result.array = np.random.rand(len(result.array))
        return result
    


class Visuals:
    def __init__(self, audio_obj: AudioType):
        self._audio_obj = audio_obj


    def waveform(self, samples = 10000):
        import matplotlib.pyplot as plt

        sr = self._audio_obj.sr
        array = self._audio_obj.array
        downsampled = array[::int(len(array) / samples)]
        t = np.linspace(0, len(downsampled)/sr, len(downsampled))

        plt.figure(figsize=(12, 4))
        plt.plot(t, downsampled)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Amplitude')
        plt.title('Waveform')
        plt.grid(True, alpha=0.3)
        plt.show()


    def spectrums(self):
        import matplotlib.pyplot as plt

        sr = self._audio_obj.sr
        array = self._audio_obj.mono().array
        spectrums = np.fft.rfft(array)
        freqs = np.fft.rfftfreq(len(array), 1/sr)
    
        plt.figure(figsize=(12, 4))
        plt.plot(freqs, np.abs(spectrums))
        plt.xlabel('Ferquancy (Hz)')
        plt.ylabel('Magnitude')
        plt.title('Spectrums')
        plt.grid(True, alpha=0.3)

        plt.show()



class Equalizer:
    def __init__(self, audio_obj: AudioType):
        self._audio_obj = audio_obj


    def custom_eq(self, start_freq, end_freq, in_range_multiplier = 1.2, out_range_multiplier = 0.8) -> AudioType:
        result = self._audio_obj.copy()
        spectrum = np.fft.rfft(result.array, axis=0)
        freqs = np.fft.rfftfreq(len(result.array), 1/result.sr)

        mask = (freqs > start_freq) & (freqs < end_freq)
        out_mask = (freqs < start_freq) | (freqs > end_freq)

        spectrum[mask] *= in_range_multiplier
        spectrum[out_mask] *= out_range_multiplier

        result.array = np.fft.irfft(spectrum, n=len(result.array), axis=0)
        return result


    def nine_band_eq(self, _0_63 = 1., _63_125 = 1., _125_250 = 1., _250_500 = 1.,
        _500_1k = 1., _1k_2k = 1., _2k_4k = 1., _4k_8k = 1., _8k_16k = 1.,) -> AudioType:
        result = self._audio_obj.copy()
        spectrum = np.fft.rfft(result.array, axis=0)
        freqs = np.fft.rfftfreq(len(result.array), 1/result.sr)

        spectrum[(0 < freqs) & (freqs < 63)] *= _0_63
        spectrum[(63 < freqs) & (freqs < 125)] *= _63_125
        spectrum[(125 < freqs) & (freqs < 250)] *= _125_250
        spectrum[(250 < freqs) & (freqs < 500)] *= _250_500
        spectrum[(500 < freqs) & (freqs < 1000)] *= _500_1k
        spectrum[(1000 < freqs) & (freqs < 2000)] *= _1k_2k
        spectrum[(2000 < freqs) & (freqs < 4000)] *= _2k_4k
        spectrum[(4000 < freqs) & (freqs < 8000)] *= _4k_8k
        spectrum[(8000 < freqs)] *= _8k_16k

        result.array = np.fft.irfft(spectrum, n=len(result.array), axis=0)
        return result

    
    def three_band_eq(self, _0_500=1., _500_2k=1., _2k_16k=1.) -> AudioType:
        result = self._audio_obj.copy()
        spectrum = np.fft.rfft(result.array, axis=0)
        freqs = np.fft.rfftfreq(len(result.array), 1/result.sr)

        spectrum[(0 < freqs) & (freqs < 500)] *= _0_500
        spectrum[(500 < freqs) & (freqs < 2000)] *= _500_2k
        spectrum[(2000 < freqs)] *= _2k_16k

        result.array = np.fft.irfft(spectrum, n=len(result.array), axis=0)
        return result


    def gui(self):
        gains = {
            "63": 1.0,
            "125": 1.0,
            "250": 1.0,
            "500": 1.0,
            "1K": 1.0,
            "2K": 1.0,
            "4K": 1.0,
            "8K": 1.0,
            "16K": 1.0
        }

        import tkinter as tk

        root = tk.Tk()
        root.title("9-Band EQ")

        bands = ["63", "125", "250", "500", "1K", "2K", "4K", "8K", "16K"]
        slider_frame = tk.Frame(root)
        slider_frame.pack(pady=20, padx=20)
        sliders = []

        for band in bands:
            frame = tk.Frame(slider_frame)
            frame.pack(side=tk.LEFT, padx=5)
            tk.Label(frame, text=band, font=('Arial', 8)).pack()
            slider = tk.Scale(frame,from_=12, to=-12,orient=tk.VERTICAL,length=200,width=30)
            slider.set(0)
            slider.pack()
            sliders.append(slider)
            
            db_label = tk.Label(frame, text="0dB", font=('Arial', 7))
            db_label.pack()
            
            def make_callback(lbl, band_name):
                def wrapper(val):
                    lbl.config(text=f"{int(float(val))}dB")
                    
                    gains[band_name] = 10 ** (int(float(val)) / 20)

                return wrapper

            slider.config(command=make_callback(db_label, band))

        root.mainloop()

        return self.nine_band_eq(*gains.values())



if __name__ == "__main__":
    ...
    a = AudioType("Audios/Lost soul down.wav")
    # a = a.eq.gui()
    print(a.channels)
    # b = AudioType("Audios/Rarin - Mamacita.wav")

    # result = a.fx.merge(b, 0.5, 0.5, 100000, 50000)
    # result.save()


