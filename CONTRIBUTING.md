# How to contribute

We're glad you're thinking about contributing to time-cord!  Here are a few guidelines to get you started.

## Things to keep in mind

### Be nice

Be nice to other people here.  Racism, sexism, etc. are not tolerated anywhere on this repository.  

### Pull from master

Generally, you want to be working with code that (mostly) already works, so pull from master and not some other development branch.  On the other hand, feel free to create your own branch when you create a PR.

### Use issues and PRs

Notice a problem with the code, or want to suggest an enhancement?  Create an issue.  And of course, code should be added with a pull request.  Also, write detailed and thoughtful commit messages, issue descriptions, etc.—at least if you have any intention for other people to read them.

### Test your code

Before submitting any PR, please try to test your code a little.  Formal tests aren't required, but please do not submit PRs with obvious syntax errors or that have obviously not been run even once.

Additionally, as much as possible, please try to avoid making PRs that cause merge conflicts.  If the repository has updated since you last pulled, use ``git rebase`` to fix that.

### Where do I start?

If you want to contribute, but don't know what to do, start by looking at the issues.  Issues marked with "good first issue" are a good place to start.  If you have questions about a particular issue, you can post them in the discussion under the issue, or email me at cyang22@andover.edu.

Right now, the biggest thing I need help with is rewriting some portions of the code so they're compatible with Windows.  

As to learn more about how this code works, keep reading!

## How does time-cord work?

time-cord is a library for **monitoring activity on Discord**.  Right now, there's basically two big chunks. The first chunk are the functions that take a _snapshot_ of current Discord activity.  The two main functions there you'll be working with are ``channel_name()`` and ``server_name()``, which use a variety of tactics to deduce current Discord channel/server.  All of this code happens inside ``monitor.py``.  The second chunk are the functions that _schedule_ snapshots to be taken at regular intervals automagically.  This happens inside both ``schedule.py``, which contains functions that will force ``run.py`` to start up whenever the computer boots.  ``run.py`` then takes a snapshot every 30 seconds or so, and writes it to ``records.log``.

### ``monitor.py``

time-cord gets the channel name by checking the name and the window title (these are different) of the "focused" application (``return_top()``).  If you're in full-screen mode, that application will be the one you're looking at.  If you have multiple windows, that application will be the one any keyboard input goes to.  Next, it checks if the application name is Discord, and if so, will return a parsed channel name (``channel_name()``).

The way time-cord gets the server name is considerably more complex.  If Discord is verified to be open, time-cord will **take a screenshot** of the Discord tab, by first computing the window bounds of Discord (``get_bounds()``) and then taking a screenshot using those bounds (``get_screenshot()``).  Then, it starts from the topmost corner and uses the colors from Discord's default palette to create a bounding box for the server name's box (which is near the top-left corner).  Finally, an OCR engine ([EasyOCR](https://github.com/JaidedAI/EasyOCR)) is used to recognize the server name (both of these happen in ``server_name()``).

### ``scheduling.py`` and ``run.py``

These two form the backbone of the scheduling function of time-cord.

In Mac OS, ``scheduling.py`` adds ``run.py`` to a [launchd](https://www.launchd.info/) task that is run on startup, and kept alive.  There is currently no Windows support for this function yet—maybe you'll be the one to add it!

``run.py`` loads the OCR engine and then runs ``record()`` every 30 seconds.  ``record()`` first takes a snapshot by computing the output of ``channel_name()`` and ``server_name()`` from ``monitor.py``, and then writes it to a new line (``rec_write()``) in ``records.log``.  Records are of the following form:
```
[current time since the epoch],[channel name / NONE if Discord isn't open],[server name / NONE if Discord isn't open]
```

### What's next for time-cord?

As of this point in development, the focus is on writing new functions that allow a user to gain insights into the logged Discord data.
