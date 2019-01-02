# transcript

Currently, this is a python program that converts the text of a play into SRT (Subrip Text) formatted subtitles. This is one of the most common formats accepted by closed captions readers, such as Youtube and VLC.

## Usage

Open a command prompt or terminal. Change into the directory where the python program is.

```
python srt_maker.py -help
```

This will output the documentation for this script.

```
python srt_maker.py <in-file> <out-file>
```

This will produce SRT subtitles in the output file based on whatever is in the input file. The input file can contain a mix of directives, SRT subtitles, and sections of a play.

If you don't care to adjust your directives in case the wrong output is produced, then you can overwrite the input file by supplying it as the output file too.

Most media players will automatically recognize the subtitles if the file containing them has the same name as the video (ex: My_movie.mp4 and My_movie.srt)

## Examples

Input file:

    @DELAY 1000
    1
    00:00:25,000 --> 00:00:26,000
    [Theme Song]
    
    <SCRIPT>
    00:00:45,100 --> 00:00:46,200
    ALEX: Knock Knock
    BARBARA: Who's there?
    ALEX: Lettuce
    @DELAY 700
    @SPEED 60
    BARBARA: Lettuce who?
    ALEX: Let me in already! I've been freezing out here.
    </SCRIPT>

Will produce the following output:

    2
    00:00:26,000 --> 00:00:27,000
    [Theme Song]
    
    3
    00:00:47,100 --> 00:00:48,200
    Knock Knock
    
    4
    00:00:49,200 --> 00:00:49,900
    Who's there?
    
    5
    00:00:50,900 --> 00:00:51,350
    Lettuce
    
    6
    00:00:52,050 --> 00:00:52,870
    Lettuce who?
    
    7
    00:00:53,570 --> 00:00:56,020
    Let me in already! I've been freezing out here.

