--[[

]] --

----- Dependencies -----
--include('karaskel.lua')
local json = require 'Pyegi.json'
local re = require 'aegisub.re'
-- local petzku = require 'petzku.util'

----- Script Info -----
script_name = "Pyegi"
script_description = "Python + Aegisub"
script_version = "0.0.2"
script_author = "DrunkSimurgh & SSgumS"
script_namespace = "Pyegi"

----- Macro Name -----
local main_macro_name = "Pyegi"

----- Variables -----
local ADP
local ADD
local APT
local dependency_dir
local settings_filepath
local default_settings = {
	python_path = ""
}

----- Functions -----
-- Source: https://stackoverflow.com/a/11130774
local function scandir(directory, filter_term)
	local i, t, popen = 0, {}, io.popen
	local pfile = popen('dir "' .. directory .. '" /b /ad')
	for dirname in pfile:lines() do
		if filter_term ~= "" then
			if dirname and re.match(string.lower(dirname), string.lower(filter_term)) then
				i = i + 1
				t[i] = dirname
			end
		else
			if dirname then
				i = i + 1
				t[i] = dirname
			end
		end
	end
	pfile:close()
	return t
end

-- get all lines from a file, returns an empty
-- list/table if the file does not exist
local function lines_from(file_path)
	local lines = {}
	for line in io.lines(file_path) do
		lines[#lines + 1] = line
	end
	return lines
end

-- get the string from a file, returns nil if the file does not exist
local function read_all_file_as_string(file_path)
	local f = assert(io.open(file_path, "rb"))
	local str = f:read("*a")
	assert(f:close())
	return str
end

local function serialize(val, name, skipnewlines, depth)
	skipnewlines = skipnewlines or false
	depth = depth or 0
	local tmp = string.rep(" ", depth)
	if name then tmp = tmp .. name .. " = " end
	if type(val) == "table" then
		tmp = tmp .. "{" .. (not skipnewlines and "\n" or "")
		for k, v in pairs(val) do
			tmp = tmp .. serialize(v, k, skipnewlines, depth + 1) .. "," .. (not skipnewlines and "\n" or "")
		end
		tmp = tmp .. string.rep(" ", depth) .. "}"
	elseif type(val) == "number" then
		tmp = tmp .. tostring(val)
	elseif type(val) == "string" then
		tmp = tmp .. string.format("%q", val)
	elseif type(val) == "boolean" then
		tmp = tmp .. (val and "true" or "false")
	else
		tmp = tmp .. "\"[inserializeable datatype:" .. type(val) .. "]\""
	end
	return tmp
end

local function cumsum_i(vector, index)
	local sum = 0
	for i = 1, index do
		sum = sum + vector[i]
	end
	return sum
end

--source: https://stackoverflow.com/a/4991602
local function file_exists(name)
	local f = io.open(name, "r")
	if f ~= nil then io.close(f) return true else return false end
end

local function macro_init() -- aegisub is nil on script's load
	ADP = aegisub.decode_path
	ADD = aegisub.dialog.display
	APT = aegisub.progress.task
	APS = aegisub.progress.set
	dependency_dir = ADP("?user") .. "/automation/dependency/Pyegi/"
	settings_filepath = dependency_dir .. "settings.json"
end

local function post_init(sub, sel)
	::MainGUI::
	-- Running main python gui
	local main_py_script_path = dependency_dir .. "Pyegi/main.py"
	local main_py_parameters_file_path = os.tmpname()
	-- aegisub.log(5, serialize(main_py_parameters_file_path) .. "\n")
	local command_parameters_string = ' "' .. main_py_script_path .. '" "' .. main_py_parameters_file_path .. '"'
	-- aegisub.log(5, serialize(command_parameters_string) .. "\n")
	APT("Waiting for user to select a python script...")
	assert(os.execute('""' .. dependency_dir .. '.venv/Scripts/python.exe" ' .. command_parameters_string .. '"'))

	if file_exists(main_py_parameters_file_path) then --TODO: address the scenarios in which this could happen
		-- Processing the selected parameters from the python main GUI
		APT("Preparing the data...")
		local main_py_parameters = json.decode(read_all_file_as_string(main_py_parameters_file_path))
		-- aegisub.log(5, serialize(main_py_parameters) .. "\n")
		local desired_lines_index = {}
		if main_py_parameters["applyOn"] == "selected lines" then
			for _, line_index in ipairs(sel) do
				table.insert(desired_lines_index, line_index)
			end
		else
			for line_index = 1, #sub do
				if sub[line_index].class == "dialogue" then
					table.insert(desired_lines_index, line_index)
				end
			end
		end

		-- Building the string resembling the current subtitle file (or only with selected line(s)) to be sent to the python script.
		local str = ""
		local info_header, style_header = true, true
		for i = 1, #sub do
			local l = sub[i]
			if l.class == "info" then
				if info_header then
					if str == "" then
						str = "[Script Info]" .. "\n" .. "; Script generated by Pyegi" .. "\n" .. "; http://www.aegisub.org/"
					else
						str = str .. "\n\n" .. "[Script Info]" .. "\n" .. "; Script generated by Pyegi" .. "\n" ..
							"; http://www.aegisub.org/"
					end
					info_header = false
				end
				str = str .. "\n" .. l.raw
			end
			if l.class == "style" then
				if style_header then
					if str == "" then
						str = "[V4+ Styles]" ..
							"\n" ..
							"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
					else
						str = str ..
							"\n\n" ..
							"[V4+ Styles]" ..
							"\n" ..
							"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
					end
					style_header = false
				end
				str = str .. "\n" .. l.raw
			end
		end
		str = str .. "\n\n" ..
			"[Events]" .. "\n" .. "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"

		-- write the created ass script
		local lua_out_file_path = os.tmpname()
		-- aegisub.log(5, serialize(lua_out_file_path) .. "\n")
		local lua_out = assert(io.open(lua_out_file_path, "wb"))
		lua_out:write(str)
		assert(lua_out:close())

		str = ""
		local str_threshold = 10000

		local desired_lines_length = #desired_lines_index
		for z, i in ipairs(desired_lines_index) do
			APS(z / desired_lines_length * 100)
			local l = sub[i]
			str = str .. "\n" .. l.raw
			if #str > str_threshold then
				lua_out = assert(io.open(lua_out_file_path, "ab"))
				lua_out:write(str)
				assert(lua_out:close())
				str = ""
			end
		end

		-- write the remaining created ass script
		if #str > 0 then
			lua_out = assert(io.open(lua_out_file_path, "ab"))
			lua_out:write(str)
			assert(lua_out:close())
			str = ""
		end

		-- Running second python gui
		local py_out_file_path = os.tmpname()
		-- aegisub.log(5, serialize(py_out_file_path) .. "\n")
		local py_script_path = dependency_dir .. "Pyegi/second.py"
		local py_parameters_file_path = os.tmpname()
		local selected_script = main_py_parameters["selectedScript"]
		local lines_parameters_file_path = os.tmpname()
		local command_parameters_string = ' "' .. py_script_path ..
			'" "' .. lua_out_file_path ..
			'" "' .. py_out_file_path ..
			'" "' .. py_parameters_file_path ..
			'" "' .. selected_script ..
			'" "' .. lines_parameters_file_path .. '"'
		-- aegisub.log(5, serialize(command_parameters_string) .. "\n")
		APT("Waiting for python results...")
		assert(os.execute('""' .. dependency_dir .. '.venv/Scripts/python.exe" ' .. command_parameters_string .. '"'))

		if file_exists(py_out_file_path) then
			-- Converting the result to ass lines.
			APT("Producing new lines...")
			local auxiliary_output = json.decode(read_all_file_as_string(lines_parameters_file_path))
			-- aegisub.log(5, serialize(auxiliary_output) .. "\n")
			if auxiliary_output["Original Lines"] == "C" then
				for _, i in ipairs(desired_lines_index) do
					local l = sub[i]
					-- Comment lines
					l.comment = true
					sub[i] = l
				end
			elseif auxiliary_output["Original Lines"] == "D" then
				for i = #desired_lines_index, 1, -1 do
					local index = desired_lines_index[i]
					sub.delete(index)
				end
				local subtracted_value = 0
				for i = 1, #desired_lines_index do
					subtracted_value = subtracted_value + 1
					desired_lines_index[i] = desired_lines_index[i] - subtracted_value
				end
			end
			local produced_lines = {}
			for i = 1, #desired_lines_index do
				produced_lines[i] = 0
			end
			local desired_lines_max = #desired_lines_index
			-- aegisub.log(5, serialize(desired_lines_index) .. "\n")
			local all_lines = lines_from(py_out_file_path)
			local new_line = {}
			local line_params_number = 11
			new_line["class"] = "dialogue"
			new_line["comment"] = false
			new_line["layer"] = 0
			new_line["start_time"] = 0
			new_line["end_time"] = 0
			new_line["style"] = ""
			new_line["actor"] = ""
			new_line["margin_l"] = 0
			new_line["margin_r"] = 0
			new_line["margin_t"] = 0
			new_line["effect"] = ""
			new_line["text"] = ""
			for counter1 = 1, (#all_lines / line_params_number) do
				local line_number = tonumber(all_lines[line_params_number * (counter1 - 1) + 1])
				new_line.layer = tonumber(all_lines[line_params_number * (counter1 - 1) + 2])
				new_line.start_time = tonumber(all_lines[line_params_number * (counter1 - 1) + 3])
				new_line.end_time = tonumber(all_lines[line_params_number * (counter1 - 1) + 4])
				new_line.style = all_lines[line_params_number * (counter1 - 1) + 5]
				new_line.actor = all_lines[line_params_number * (counter1 - 1) + 6]
				new_line.margin_l = tonumber(all_lines[line_params_number * (counter1 - 1) + 7])
				new_line.margin_r = tonumber(all_lines[line_params_number * (counter1 - 1) + 8])
				new_line.margin_t = tonumber(all_lines[line_params_number * (counter1 - 1) + 9])
				new_line.effect = all_lines[line_params_number * (counter1 - 1) + 10]
				new_line.text = all_lines[line_params_number * (counter1 - 1) + 11]
				if (line_number < 0) or (auxiliary_output["Placement"] == "S") then
					sub.insert(1, new_line)
					produced_lines[1] = produced_lines[1] + 1
				elseif (line_number > desired_lines_max) or (auxiliary_output["Placement"] == "E") then
					sub[0] = new_line
				else
					sub.insert(desired_lines_index[line_number] + cumsum_i(produced_lines, line_number) + 1, new_line)
					produced_lines[line_number] = produced_lines[line_number] + 1
				end
			end
		else
			goto MainGUI
		end
	end
end

function Main(sub, sel)
	macro_init()
	post_init(sub, sel)

	aegisub.set_undo_point(main_macro_name)
end

-- Register the macro
aegisub.register_macro(main_macro_name, script_description, Main)
