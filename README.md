# vtc commands project
The aim of this project is to extend the existing in-house developed command line tool used by VASTech. This will allow a user to view system events and alarms from the console if they do not have access to the GUI.

The added functionality is as follows:
  - Retrieve entries from a predefined MySQL database, permorming simple SQL queries based on the command line parameters given to the application
  - Format the query output result for the command line

This functionality is developed in Python and makes use of the [Click] library. 

## How to use the functionality
There is already a group of "cp" commands present in the command line tool. The commands developed for this project will comprise the "sp" group of commands. To use, then, one would type into the command line:

```sh
$ vtc sp
```

followed by one of the commands being developed:
  - `alarms`
  - `sysevents`
  - `services`

and an option:
  - `--host`
  - `--severity`
  - `--since`
  - `--output`
  - `--state`
  - `--serviceinskey`
  - `--event`

Not all options are available for all commands. Each option has a predefined set of constant values it can take. For example, the `--host` command can take on the values `all` or the specific hostname desired.

When run from the command line it looks something like this:
```
$ vtc sp alarms --host=orc45
```
The alarms corresponding to the host "orc45" are then displayed in table format, since an output format has not been specified. 

If an invalid value for an option is input, the output will be "Invalid value for option", except if an invalid date is input, in which case the output will be "Invalid date".

Typing in `--help` after `sp` will show which commands are available, and what they do. Typing it in after one of the commands will give a description of what options are available for that command, and what their functions are.

At the moment, the entire command line interface is contained in one file, `vtc.py`, which was converted to a script using [setuptools].

A brief description of each command and its options is given below.

### alarms
This command displays information about various alarms.
Available options are: `--host=all|hostname` (hostname -> the name of a specific host), `--severity=all|warning|critical`, `--since=current|yesterday|utc-time` (utc-time -> the time in the format yyyy-mm-dd_hh:mm:ss), `--output=table|simple|json`, `--serviceinskey=all|keyvalue` (keyvalue -> the value of a service instance key).

Special information about the options:
  - If `--since=utc-time` is chosen, the user *must* type in the date, however the time is not essential to input. The underscore between date and time is also essential for the interface to recognise it as one argument.

### sysevents
This command displays information about system events.
Available options are: `--host=all|hostname` (hostname -> the name of a specific host), `--severity=all|warning|info|critical`, `--since=current|yesterday|utc-time` (utc-time -> the time in the format yyyy-mm-dd_hh:mm:ss), `--output=table|simple|json`, `--event=all|action` (action -> a type of event, e.g. Alarm_Raise), `--serviceinskey=all|keyvalue` (keyvalue -> the value of a service instance key).

Special information about the options:
  - If `--since=utc-time` is chosen, the user *must* type in the date, however the time is not essential to input. The underscore between date and time is also essential for the interface to recognise it as one argument.

### services
This command displays information about services running on the system.
Available options are: `--host=all|hostname` (hostname -> the name of a specific host), `--state=all|running|stopped`, `--output=table|simple|json`, `--serviceinskey=all|keyvalue` (keyvalue -> the value of a specific service instance key).

## SQL interface
The SQL interface is contained in the `readsql.py` file. It uses the "MySQL Connector" driver to connect to a database. The database can be specified via the `db` variable. 

A function makes a connection to the desired database, and then queries corresponding to the commands and options are made to the database. For the `vtc.py` file to use these functions, `readsql` is imported and then the appropriate functions are called with appropriate arguments, according to the commands and queries being processed. The results are then displayed in the command line console. 
-
The formatting of the output is also done in the `readsql.py` file. The [pandas] library is used to help with formatting, as it provides easy methods to convert the results of a SQL query to tables or json. 

For each command, there is a function that collects data from the corresponding query. This query is constructed with a query builder function. 

## Output
The output can be formatted three ways: simple, json and table. In the table, all columns are shown with headings. Simple mode usually displays fewer columns, without headings. Json is self-explanatory. If a field is used to filter the data, that field value will not be shown as a column in the output.

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [click]: <https://click.palletsprojects.com/en/7.x/>
   [setuptools]: <https://setuptools.readthedocs.io/en/latest/>
   [pandas]: <https://pandas.pydata.org/pandas-docs/stable>
