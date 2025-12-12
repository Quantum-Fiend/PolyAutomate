# Example Ruby Plugin: File Watcher
# Monitors a directory for file changes

require 'json'

class FileWatcherPlugin
  attr_reader :name, :version, :author
  
  def initialize
    @name = "File Watcher"
    @version = "1.0.0"
    @author = "OmniTasker"
  end
  
  def watch_directory(path, duration = 10)
    puts "👀 Watching directory: #{path}"
    puts "Duration: #{duration} seconds"
    
    unless Dir.exist?(path)
      return {
        status: 'error',
        message: "Directory does not exist: #{path}"
      }
    end
    
    # Get initial file list
    initial_files = Dir.glob("#{path}/**/*").select { |f| File.file?(f) }
    puts "Initial files: #{initial_files.length}"
    
    # Wait
    sleep(duration)
    
    # Get final file list
    final_files = Dir.glob("#{path}/**/*").select { |f| File.file?(f) }
    
    # Detect changes
    added = final_files - initial_files
    removed = initial_files - final_files
    
    result = {
      status: 'success',
      initial_count: initial_files.length,
      final_count: final_files.length,
      added: added,
      removed: removed,
      changes_detected: added.any? || removed.any?
    }
    
    puts "\n📊 Results:"
    puts "Added: #{added.length} files"
    puts "Removed: #{removed.length} files"
    
    result
  end
  
  def plugin_info
    {
      name: @name,
      version: @version,
      author: @author
    }
  end
end

# Main execution
if __FILE__ == $0
  watcher = FileWatcherPlugin.new
  
  # Default to watching /tmp for 10 seconds
  watch_path = ARGV[0] || '/tmp'
  duration = (ARGV[1] || 10).to_i
  
  result = watcher.watch_directory(watch_path, duration)
  puts "\n✅ Plugin execution completed"
  puts JSON.pretty_generate(result)
end
