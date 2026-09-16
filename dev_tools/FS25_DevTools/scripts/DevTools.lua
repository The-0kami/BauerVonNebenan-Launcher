DevTools = DevTools or {}

DevTools.MOD_NAME = g_currentModName or "FS25_DevTools"
DevTools.LOG_PREFIX = "[DevTools:ObjectInspector]"
DevTools.RAYCAST_DISTANCE = 30
DevTools.MAX_PARENT_DEPTH = 8
DevTools.lastHit = nil
DevTools.actionEventIds = {}

local function logInfo(message, ...)
    Logging.info("%s %s", DevTools.LOG_PREFIX, string.format(message, ...))
end

local function logWarning(message, ...)
    Logging.warning("%s %s", DevTools.LOG_PREFIX, string.format(message, ...))
end

local function safeCall(label, fn, ...)
    if fn == nil then
        return "<function unavailable>"
    end

    local ok, a, b, c, d = pcall(fn, ...)
    if not ok then
        return string.format("<error: %s>", tostring(a))
    end

    if b ~= nil or c ~= nil or d ~= nil then
        local values = {a, b, c, d}
        local result = {}
        for _, value in ipairs(values) do
            if value ~= nil then
                table.insert(result, tostring(value))
            end
        end
        return table.concat(result, ", ")
    end

    return tostring(a)
end

local function getNodeName(nodeId)
    if nodeId == nil or nodeId == 0 or not entityExists(nodeId) then
        return "<invalid>"
    end

    local ok, name = pcall(getName, nodeId)
    if ok and name ~= nil and name ~= "" then
        return name
    end

    return "<unnamed>"
end

local function getNodeObjectDescription(nodeId)
    if g_currentMission == nil or g_currentMission.getNodeObject == nil then
        return "<mission node lookup unavailable>"
    end

    local ok, object = pcall(g_currentMission.getNodeObject, g_currentMission, nodeId)
    if not ok then
        return string.format("<lookup error: %s>", tostring(object))
    end

    if object == nil then
        return "<none>"
    end

    local parts = {tostring(object)}

    if object.getName ~= nil then
        local nameOk, name = pcall(object.getName, object)
        if nameOk and name ~= nil and name ~= "" then
            table.insert(parts, "name=" .. tostring(name))
        end
    end

    if object.configFileName ~= nil then
        table.insert(parts, "config=" .. tostring(object.configFileName))
    end

    if object.rootNode ~= nil then
        table.insert(parts, "rootNode=" .. tostring(object.rootNode))
    elseif object.nodeId ~= nil then
        table.insert(parts, "nodeId=" .. tostring(object.nodeId))
    end

    return table.concat(parts, " | ")
end

function DevTools:notify(message, isError)
    if g_currentMission == nil then
        return
    end

    local notificationType = FSBaseMission.INGAME_NOTIFICATION_OK
    if isError then
        notificationType = FSBaseMission.INGAME_NOTIFICATION_CRITICAL
    end

    g_currentMission:addIngameNotification(notificationType, message)
end

function DevTools:dumpNode(nodeId, hitData, repeated)
    if nodeId == nil or nodeId == 0 or not entityExists(nodeId) then
        logWarning("Cannot dump invalid node '%s'", tostring(nodeId))
        self:notify("Dev Tools: Ungültiger Node", true)
        return
    end

    local separator = string.rep("=", 76)
    Logging.info("%s", separator)
    Logging.info("%s OBJECT DUMP%s", self.LOG_PREFIX, repeated and " (REPEAT)" or "")
    Logging.info("%s nodeId: %s", self.LOG_PREFIX, tostring(nodeId))
    Logging.info("%s nodeName: %s", self.LOG_PREFIX, getNodeName(nodeId))

    if hitData ~= nil then
        Logging.info("%s hitPosition: %.4f, %.4f, %.4f", self.LOG_PREFIX, hitData.x or 0, hitData.y or 0, hitData.z or 0)
        Logging.info("%s distance: %.4f", self.LOG_PREFIX, hitData.distance or -1)
        Logging.info("%s normal: %.4f, %.4f, %.4f", self.LOG_PREFIX, hitData.nx or 0, hitData.ny or 0, hitData.nz or 0)
        Logging.info("%s subShapeIndex: %s", self.LOG_PREFIX, tostring(hitData.subShapeIndex))
        Logging.info("%s shapeId: %s", self.LOG_PREFIX, tostring(hitData.shapeId))
    end

    Logging.info("%s rigidBodyType: %s", self.LOG_PREFIX, safeCall("getRigidBodyType", getRigidBodyType, nodeId))
    Logging.info("%s hasCollision: %s", self.LOG_PREFIX, safeCall("getHasCollision", getHasCollision, nodeId))
    Logging.info("%s hasTrigger: %s", self.LOG_PREFIX, safeCall("getHasTrigger", getHasTrigger, nodeId))
    Logging.info("%s addedToPhysics: %s", self.LOG_PREFIX, safeCall("getIsAddedToPhysics", getIsAddedToPhysics, nodeId))
    Logging.info("%s isCompound: %s", self.LOG_PREFIX, safeCall("getIsCompound", getIsCompound, nodeId))
    Logging.info("%s isCompoundChild: %s", self.LOG_PREFIX, safeCall("getIsCompoundChild", getIsCompoundChild, nodeId))

    local filterOk, group, mask = pcall(getCollisionFilter, nodeId)
    if filterOk then
        Logging.info("%s collisionGroup: %s", self.LOG_PREFIX, tostring(group))
        Logging.info("%s collisionMask: %s", self.LOG_PREFIX, tostring(mask))
        Logging.info("%s collisionGroupHex: 0x%X", self.LOG_PREFIX, tonumber(group) or 0)
        Logging.info("%s collisionMaskHex: 0x%X", self.LOG_PREFIX, tonumber(mask) or 0)
    else
        Logging.info("%s collisionFilter: <error: %s>", self.LOG_PREFIX, tostring(group))
    end

    Logging.info("%s missionNodeObject: %s", self.LOG_PREFIX, getNodeObjectDescription(nodeId))

    Logging.info("%s parentChain:", self.LOG_PREFIX)
    local currentNode = nodeId
    for depth = 0, self.MAX_PARENT_DEPTH do
        if currentNode == nil or currentNode == 0 or not entityExists(currentNode) then
            break
        end

        Logging.info("%s   [%d] id=%s name='%s' rigidBodyType=%s", self.LOG_PREFIX, depth, tostring(currentNode), getNodeName(currentNode), safeCall("getRigidBodyType", getRigidBodyType, currentNode))

        local parentOk, parentNode = pcall(getParent, currentNode)
        if not parentOk or parentNode == nil or parentNode == 0 or parentNode == currentNode then
            break
        end

        currentNode = parentNode
    end

    Logging.info("%s", separator)

    self.lastHit = {
        nodeId = nodeId,
        hitData = hitData
    }

    self:notify(string.format("Dev Tools: Node %s in log.txt geschrieben", tostring(nodeId)), false)
end

function DevTools:onRaycastHit(nodeId, x, y, z, distance, nx, ny, nz, subShapeIndex, shapeId, isLast)
    if nodeId == nil or nodeId == 0 then
        return true
    end

    self:dumpNode(nodeId, {
        x = x,
        y = y,
        z = z,
        distance = distance,
        nx = nx,
        ny = ny,
        nz = nz,
        subShapeIndex = subShapeIndex,
        shapeId = shapeId
    }, false)

    return false
end

function DevTools:inspectObject()
    if g_localPlayer == nil then
        logWarning("No local player available")
        self:notify("Dev Tools: Kein lokaler Spieler verfügbar", true)
        return
    end

    local cameraNode = g_localPlayer:getCurrentCameraNode()
    if cameraNode == nil or cameraNode == 0 or not entityExists(cameraNode) then
        logWarning("No valid player camera node available")
        self:notify("Dev Tools: Keine gültige Kamera gefunden", true)
        return
    end

    local x, y, z = getWorldTranslation(cameraNode)
    local dx, dy, dz = localDirectionToWorld(cameraNode, 0, 0, -1)
    dx, dy, dz = MathUtil.vector3Normalize(dx, dy, dz)

    logInfo("Inspect ray fired from %.3f %.3f %.3f direction %.3f %.3f %.3f", x, y, z, dx, dy, dz)

    local hitCount = raycastClosest(
        x, y, z,
        dx, dy, dz,
        self.RAYCAST_DISTANCE,
        "onRaycastHit",
        self
    )

    if hitCount == nil or hitCount == 0 then
        logInfo("Raycast returned no rigid-body hit within %sm", tostring(self.RAYCAST_DISTANCE))
        self:notify(string.format("Dev Tools: Kein Objekt innerhalb %sm getroffen", tostring(self.RAYCAST_DISTANCE)), true)
    end
end

function DevTools:repeatLastDump()
    if self.lastHit == nil or self.lastHit.nodeId == nil then
        self:notify("Dev Tools: Noch kein Objekt-Dump vorhanden", true)
        return
    end

    if not entityExists(self.lastHit.nodeId) then
        logWarning("Last node %s no longer exists", tostring(self.lastHit.nodeId))
        self:notify("Dev Tools: Letzter Node existiert nicht mehr", true)
        self.lastHit = nil
        return
    end

    self:dumpNode(self.lastHit.nodeId, self.lastHit.hitData, true)
end

function DevTools:onInspectAction(actionName, inputValue, callbackState, isAnalog)
    self:inspectObject()
end

function DevTools:onRepeatAction(actionName, inputValue, callbackState, isAnalog)
    self:repeatLastDump()
end

function DevTools:registerActionEvents()
    if g_inputBinding == nil then
        logWarning("Input binding system not available")
        return
    end

    self:removeActionEvents()

    local successInspect, inspectId = g_inputBinding:registerActionEvent(
        InputAction.DEVTOOLS_INSPECT_OBJECT,
        self,
        self.onInspectAction,
        false,
        true,
        false,
        true
    )

    if successInspect then
        self.actionEventIds.inspect = inspectId
        g_inputBinding:setActionEventTextVisibility(inspectId, false)
    else
        logWarning("Failed to register DEVTOOLS_INSPECT_OBJECT action")
    end

    local successRepeat, repeatId = g_inputBinding:registerActionEvent(
        InputAction.DEVTOOLS_REPEAT_DUMP,
        self,
        self.onRepeatAction,
        false,
        true,
        false,
        true
    )

    if successRepeat then
        self.actionEventIds.repeatDump = repeatId
        g_inputBinding:setActionEventTextVisibility(repeatId, false)
    else
        logWarning("Failed to register DEVTOOLS_REPEAT_DUMP action")
    end

    logInfo("Action events registered. Inspect=%s Repeat=%s", tostring(successInspect), tostring(successRepeat))
end

function DevTools:removeActionEvents()
    if g_inputBinding == nil then
        return
    end

    for _, actionEventId in pairs(self.actionEventIds) do
        if actionEventId ~= nil then
            g_inputBinding:removeActionEvent(actionEventId)
        end
    end

    self.actionEventIds = {}
end

function DevTools:loadMap(mapName)
    logInfo("Loaded on map '%s'", tostring(mapName))
    self.lastHit = nil
    self:registerActionEvents()
end

function DevTools:deleteMap()
    logInfo("Unloading")
    self:removeActionEvents()
    self.lastHit = nil
end

addModEventListener(DevTools)
