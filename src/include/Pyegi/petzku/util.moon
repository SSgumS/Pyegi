[[
README

A bunch of different utility functions I use all over the place.
Or maybe I don't. But that's the plan, at least.

Anyone else is free to use this library too, but most of the stuff is specifically for my own stuff.
]]

util = require "aegisub.util"
re = require "aegisub.re"

-- "\" on windows, "/" on any other system
pathsep = package.config\sub 1,1

lib = {}
with lib
    [[
    .util = {
        serialize: (value, name, skip_newlines=false, depth=0) ->
            tmp = string.rep(" ", depth)
            if name
                tmp = tmp .. name .. " = "
            if type(value) == "table"
                tmp = tmp .. "{" .. (not skip_newlines and "\n" or "")
                for k, v in pairs(value)
                    tmp = tmp .. .util.serialize(v, k, skip_newlines, depth + 1) .. "," .. (not skip_newlines and "\n" or "")
                tmp = tmp .. string.rep(" ", depth) .. "}"
            elseif type(value) == "number"
                tmp = tmp .. tostring(value)
            elseif type(value) == "string"
                tmp = tmp .. string.format("%q", value)
            elseif type(value) == "boolean"
                tmp = tmp .. (value and "true" or "false")
            else
                tmp = tmp .. "\"[inserializeable datatype:" .. type(value) .. "]\""
            tmp
    }
    ]]

    .io = {
        :pathsep,
        run_cmd: (cmd, quiet) ->
            aegisub.log 5, 'Running: %s\n', cmd unless quiet

            local runner_path
            output_path = os.tmpname()
            if pathsep == '\\'
                -- windows
                -- command lines over 256 bytes don't get run correctly, make a temporary file as a workaround
                runner_path = aegisub.decode_path('?temp' .. pathsep .. 'petzku.bat')
                wrapper_path = aegisub.decode_path('?temp' .. pathsep .. 'petzku-wrapper.bat')
                exit_code_path = os.tmpname()
                -- provided by https://sourceforge.net/projects/unxutils/
                tee_path = "#{re.match(debug.getinfo(1).source, '@?(.*[/\\\\])')[1].str}util/tee"
                -- create wrapper
                f = io.open wrapper_path, 'w'
                f\write "@echo off\n"
                f\write "call %*\n"
                f\write "echo %errorlevel% >\"#{exit_code_path}\"\n"
                f\close!
                -- create batch script
                f = io.open runner_path, 'w'
                f\write "@echo off\n"
                f\write "call \"#{wrapper_path}\" #{cmd} 2>&1 | \"#{tee_path}\" \"#{output_path}\"\n"
                f\write "set /p errorlevel=<\"#{exit_code_path}\"\n"
                f\write "exit /b %errorlevel%\n"
                f\close!
            else
                runner_path = aegisub.decode_path('?temp' .. pathsep .. 'petzku.sh')
                pipe_path = os.tmpname()
                -- create shell script
                f = io.open runner_path, 'w'
                f\write "#!/bin/sh\n"
                f\write "mkfifo \"#{pipe_path}\"\n"
                f\write "tee \"#{output_path} <\"#{pipe_path}\" &\n"
                f\write "#{cmd} >\"#{pipe_path}\" 2>&1\n"
                f\write "exit $?\n"
                f\close!
                -- make the script executable
                os.execute "chmod +x \"#{runner_path}\""

            
            status, reason, exit_code = os.execute runner_path

            f = io.open output_path
            output = f\read '*a'
            f\close!

            unless quiet
                local log_level
                if status
                    log_level = 5
                else
                    log_level = 1
                aegisub.log log_level, "Command Logs: \n\n"
                aegisub.log log_level, output
                aegisub.log log_level, "\n\nStatus: "
                if status
                    aegisub.log log_level, "success\n"
                else
                    aegisub.log log_level, "failed\n"
                    aegisub.log log_level, "Reason: #{reason}\n"
                    aegisub.log log_level, "Exit Code: #{exit_code}\n"
                aegisub.log log_level, '\nFinished: %s\n', cmd

            output, status, reason, exit_code
    }

return lib
