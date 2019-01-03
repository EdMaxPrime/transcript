# transcript

Currently, this is a python program that converts the text of a play into SRT (Subrip Text) formatted subtitles. This is one of the most common formats accepted by closed captions readers, such as Youtube and VLC.

## Usage

Open a command prompt or terminal. Change into the directory where the python program is.

```
python srt_maker.py -help
```

The above command will output the documentation for this script.

```
python srt_maker.py <in-file> <out-file>
```

The above command will produce SRT subtitles in the output file based on whatever is in the input file. The input file can contain a mix of directives, SRT subtitles, and sections of a play. Both files must be in UTF-8 encoding.

If you don't care to adjust your directives in case the wrong output is produced, then you can overwrite the input file by supplying it as the output file too.

Most media players will automatically recognize the subtitles if the file containing them has the same name as the video (ex: My_movie.mp4 is the video and My_movie.srt is the subtitle)

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
    00:00:46,100 --> 00:00:47,200
    Knock Knock
    
    4
    00:00:47,200 --> 00:00:47,800
    Who's there?
    
    5
    00:00:47,800 --> 00:00:48,150
    Lettuce
    
    6
    00:00:48,850 --> 00:00:49,570
    Lettuce who?
    
    7
    00:00:49,570 --> 00:00:51,920
    Let me in already! I've been freezing out here.

## Directives

Note: all directives **must** be on their own lines. No whitespace, leading or trailing, is allowed.

`@OFFSET <millis>` pushes back all subsequent subtitles by the time given in milliseconds. The number of milliseconds can be positive or negative, and 0 means that the times hardcoded in the file will be used instead.

`@DELAY <millis>` this adjusts the time offset by the given amount of milliseconds. The number of milliseconds can be positive or negative, but 0 has no effect.

`@SPEED <millis>` this adjusts the duration calculation for the next subtitle. If no end time is specified for any subtitle, the formula `number_of_characters_in_subtitle_text * speed` is used. This speed directive changes the speed factor from the default one to another amount.

`@SPEED = <millis>` sets the default speed factor to the specified number of milliseconds. Default is 50.

`@GAP <millis>` sets the gap between subtitles in milliseconds. By default this is 0

`<SCRIPT>` starts a script section where lines are in the format:

    JULIET: Oh Romeo,
    Where art thou?
    ROMEO: Right here

If you want the name of the speaker to be kept, use `<SCRIPT names>` instead, because otherwise the names will be chopped off. To end the script section, use the directive `</SCRIPT>`. Note: the opening script tag must be followed by the start and end time just like a normal subtitle would be.

## Times

A normal SRT subtitle has this format:

    1
    00:00:00,000 --> 00:00:00,900
    Text here

If you're not sure what the end time is and would like it to be calculated based on the text, you can leave out the time after the arrow. If you're not sure what the start time is and would like it to be calculated based on the gap setting, leave out the time before the arrow. Both times can be absent. All times follow the format HH:MM:SS,LLL where LLL is the milliseconds. Note the comma instead of a colon.
