# get-metars

Simple command line tool to download METAR's and TAF's for a given station and
store them in text files.

## Requirements

This package requires:

* [Python ^3.7][python-home]

[python-home]: https://www.python.org

Python because it was developed on that version.

## Installation

For install only run this command from your terminal

```
pip install get-metars
```

### Update

Update with `pip` adding the option --upgrade

```
pip install --upgrade get-metars
```

## Examples

The data are downloaded from [Ogimet.com][ogimet-home], so be nice and don't saturate
the server. This site only accepts requests of data of 31 days or less at a time.

[ogimet-home]: http://ogimet.com

To download data for a specific month (i.e. january 2022) of JFK INT. Airport only run 

```
get-metars kjfk --init 2022-01-01
```

The program will understand that you want all data of the month.

If you need only the METAR's run

```
get-metars kjfk --init 2022-01-01 --type SA
```

where `SA` means `METAR` type of aeronautical report. Type `get-metars --help` to see all
the available options.

If you need a specific time of period you need to give the initial and final datetimes,
as follows

```
get-metars kjfk --init 2021-12-05T01:00:00 --final 2021-12-10T22:30:00 --type SP
```

where `SP` means `SPECI` type of aeronautical reports.

To standarize the reports for TAF-VER verification program add the flag `--sanitize` or `-s`.
To make the program store the reports in one line add the flag `--one-line` or `-o`.
By default, reports are written to the file with the datetime prefix with format `%Y%m%d%H%M`. If you
want to remove that prefix add the flag `--no-datetime-prefix`.

So that's it. Simple no?
Have a happy coding :D