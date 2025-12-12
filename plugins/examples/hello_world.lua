-- Example Lua Plugin: Hello World
-- Demonstrates basic plugin structure

-- Plugin metadata
plugin = {
    name = "Hello World",
    version = "1.0.0",
    author = "OmniTasker",
    description = "A simple hello world plugin"
}

-- Main function
function main(args)
    print("Hello from Lua plugin!")
    
    if args and args.name then
        print("Hello, " .. args.name .. "!")
    end
    
    return {
        status = "success",
        message = "Plugin executed successfully",
        timestamp = os.time()
    }
end

-- Utility function
function get_plugin_info()
    return plugin
end

-- Execute main if running standalone
if arg and arg[0] then
    local result = main()
    print("Result: " .. result.message)
end
