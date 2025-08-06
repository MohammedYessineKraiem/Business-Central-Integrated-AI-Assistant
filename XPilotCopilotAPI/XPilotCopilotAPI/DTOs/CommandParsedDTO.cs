using System.Collections.Generic;

public class CommandParsedDTO
{
    public string Action { get; set; } = string.Empty;
    public string Entity { get; set; } = string.Empty;
    public Dictionary<string, object> Parameters { get; set; } = new Dictionary<string, object>();
}
