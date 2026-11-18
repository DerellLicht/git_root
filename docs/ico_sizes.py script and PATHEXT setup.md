# Reading icon sizes (ico_sizes.py) and setting default assoc. for .py files

## You

Greetings, master!!  I would request of you, another python script...
I have a large collection of `.ico` files, I am winnowing those that are of less value to me...
What I would wish, is to be able to read a `.ico` file, and display a list of the various image sizes that are present in it... 

Actually, it would be very helpful if it would accept a folder name on the command line, and provide this information for all `.ico` files in that folder... 

Could ye provide this for me??

## Claude

Working on it: a dependency-free script that reads the ICO headers directly.

Now I'll generate test icons (BMP and PNG-compressed entries) and run it.

Your script is `ico_sizes.py`. I tested it on sample icons with mixed BMP and PNG entries, a corrupt file, and a missing folder. It needs only the standard library and reads the ICO headers directly.

```
python ico_sizes.py C:\icons
python ico_sizes.py -r C:\icons          (also search subfolders)
python ico_sizes.py a.ico b.ico C:\more  (files and folders can be mixed)
```

Each file gets one line with the image count and its sizes, sorted smallest first:

```
C:\icons\multi.ico   [3]  16x16x32, 32x32x32, 256x256x32 (PNG)
C:\icons\bad.ico         ERROR: not an ICO file (bad header)
```

- **Format:** `WxHxBits` is width, height and color depth. `(PNG)` marks Vista-style compressed entries, usually the 256×256 one.
- **256-pixel entries:** ICO stores 256 as 0, and the script translates that back to 256.
- **Sizes and depths:** Sizes and depths come from the image data itself when the directory entry is blank or unreliable.
- **Bad files:** Unreadable or corrupt files are reported as errors and the scan carries on. A summary count appears at the end.

If it would help the winnowing, I can add a filter such as "only show files lacking a 256×256 image" or "only files with fewer than N sizes".

## You

Well, that immediately and clearly answered the immediate question that I had...
I have an older folder tree of .ico files named `computer`, with subfolders for types of devices...
I suspected, due to the age of the folder, that they probably were single-size, low-resolution icons... and indeed, they are all 32x32x8, single-image files... so I can just let that go...

Thank you so much!!!

## Claude

You're very welcome, Derell! A tree of old 32x32x8 singles is exactly what a folder of that age would hold, so it's good to know for certain and be done with it. The script will be there if another icon folder needs the same check.

Happy winnowing!

## You

Okay, this is superb!!!  I would like one more assist... at some point, I lost the association of `.py` files with python... I would like to be able to run the script from the command line *without* having to include `python`; for example: `ico_sizes.py .` ... I'm on Windows 10 ... what is the simplest way to do this??

## Claude

The simplest way is to repair the association and add `.PY` to `PATHEXT`. Windows needs both for `ico_sizes.py .` to work without typing `python`.

**1. Repair the association.** Open a command prompt as Administrator and check what's currently set:

```
assoc .py
ftype Python.File
```

If either is missing or wrong, set them:

```
assoc .py=Python.File
ftype Python.File="C:\Windows\py.exe" "%L" %*
```

This uses the `py.exe` launcher that the python.org installer puts in `C:\Windows`. Check with `where py`. If you don't have it, point `ftype` at your `python.exe` instead:

```
ftype Python.File="C:\Path\To\python.exe" "%L" %*
```

The `%*` matters. Without it the script runs but your arguments (the folder name) get dropped.

**2. Add `.PY` to `PATHEXT`.** This is the step that lets you omit the extension, and it also makes cmd treat `.py` as runnable. Run this in a normal prompt:

```
setx PATHEXT "%PATHEXT%;.PY"
```

Then open a new command window, because the current one won't see the change.

After that, `ico_sizes.py .` works from any folder, provided the script's folder is on your `PATH`. Otherwise it only works from the folder where the script lives. A single `C:\bin` or similar on `PATH` for your scripts handles that.

If you'd rather skip the manual commands, re-running the Python installer and choosing Modify gets the association back. Tick "py launcher" and "Associate files with Python". Make sure the installer's "Add Python to environment variables" box is ticked too, so `PATH` is covered. It won't add `.PY` to `PATHEXT` though, so you still need step 2.

## You

Okay, those worked nicely, and `ico_sizes.py .`  works as desired... very nice...

One question; you said the PATHEXT change would also let me omit the `.py` extension; presumably that means that  `ico_sizes .`  would work... but it does not; I just get `TCC: Unknown command "ico_sizes"` ... perhaps I should have mentioned that I use `tcc.exe`, not `cmd.exe` ... though they *should* interpret these variables identically... my current PATHEXT is:

```
D:\icons Yes, Master?? > echo %PATHEXT%
.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.PY
```

Is there something else that I'm missing, or does this just not work with `tcc/le`??

Mind you, this last detail isn't that important to me; when I type part of the filename and hit TAB, it matches the entire name anyway - I'm just curious about the details here...

## Claude

It's not you. TCC only consults `PATHEXT` when its own `PathExt` configuration option is turned on. If the PathExt option is set, TCC will search the current directory and then each directory listed in PATH for a file whose extension matches one in PATHEXT. It's off by default, so TCC ignores the variable you set. `cmd.exe` always honors `PATHEXT`, which is why I expected it to work. TCC's behavior differs here, and I should have asked which shell you use.

To switch it on, either of these should work. I haven't verified the exact dialog location:

- Run `option //PathExt=Yes` at the prompt, or
- Open `OPTION` and look for PathExt in the dialog, or add `PathExt=Yes` to your TCC `.ini` file to make it permanent.

The `PATHEXT` variable you already set is the right list, and TCC will use it once the option is on.

There's also a TCC-only alternative that skips `PATHEXT` entirely. TCC lets you define executable extensions with `SET`, written as `set .ext=command [options]`. These work only when you type the extension, though, so `ico_sizes.py .` already works through your association, and neither mechanism helps you drop the `.py` without `PathExt`.

## You

Okay, perfect!!  Adding `option //PathExt=Yes` to my 4start.bat file, solved the problem quite nicely!!  and again, it's not really all that important, but it *is* cute!!

I love the fact that, even though I've been using 4dos/4nt/tcc/tcc.le since MSDOS in the late 1980s, I *still* find new things to configure in it!!!  I am also grateful that you are here for me to ask, because tcc/le is an abandonware product, and JpSoft provides no formal support for it...

## Claude

Glad it worked. Putting the option in `4start.bat` is the right place for it, since it runs on every TCC startup.

Nearly four decades of 4DOS/4NT/TCC and it still has unexplored corners, which says something about how deep that tool is. TCC/LE does still have its documentation online. The help pages I found this from (jpsoft.com/help) cover the full TCC command and option set, and most of it applies to LE. They're a good place to browse when you're curious about other `OPTION` directives, and I'm happy to dig through them with you whenever something else comes up.
