local function CsvEscape(s)
  if s == nil then return "" end
  s = tostring(s) -- This line solves the problem!
  if s:find("[,\"]") then
    return '"' .. s:gsub('"', '""') .. '"'
  else
    return s
  end
end
-- Get map (theater) name using MOOSE, MIST, or fallback
local mapName = "UnknownMap"
--[[
if mist and mist.DBs and mist.DBs.missionData and mist.DBs.missionData.theatre then
    mapName = mist.DBs.missionData.theatre
elseif UTILS and UTILS.GetDCSMap then
    mapName = UTILS.GetDCSMap()
end
--]]
mapName = UTILS.GetDCSMap()

local function WriteAirbaseCsv()
  local filename = lfs.writedir() .. "/Logs/AirbasesList_" .. mapName .. ".csv"
  local f = io.open(filename, "w")
  if not f then
    env.error("Cannot write to: " .. filename)
    return
  end

  f:write("ID,Name,Category,Coalition,Lat,Lon\n")

  -- Collect all airbases into a table first
  local airbaseList = {}
  local airbases = _DATABASE.AIRBASES
  for name, airbase in pairs(airbases) do
    if airbase then
      local airbaseName = airbase.GetName and airbase:GetName() or ""
      table.insert(airbaseList, {name = airbaseName, data = airbase})
    end
  end
  
  -- Sort airbases alphabetically by name
  table.sort(airbaseList, function(a, b)
    return a.name:upper() < b.name:upper()
  end)
  
  -- Write sorted airbases to CSV
  for _, entry in ipairs(airbaseList) do
    local airbase = entry.data
    local id = airbase.GetID and airbase:GetID() or ""
    local airbaseName = entry.name
    local category = airbase.GetCategoryName and airbase:GetCategoryName() or ""
    local coalition = airbase.GetCoalition and airbase:GetCoalition() or 0
    local coalitionStr = UTILS.GetCoalitionName and UTILS.GetCoalitionName(coalition) or ""
    local lat, lon = "", ""

    if airbase.GetPoint then
      local pt = airbase:GetPoint()
      if pt then
        lat = pt.z or ""
        lon = pt.x or ""
      end
    end

    f:write(string.format("%s,%s,%s,%s,%s,%s\n",
      CsvEscape(id),
      CsvEscape(airbaseName),
      CsvEscape(category),
      CsvEscape(coalitionStr),
      tostring(lat),
      tostring(lon)
    ))
  end

  f:close()
  env.info("Airbase/FARP list exported to " .. filename)
end

SCHEDULER:New(nil, WriteAirbaseCsv, {}, 10)
