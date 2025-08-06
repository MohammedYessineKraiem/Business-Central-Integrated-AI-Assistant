namespace XPilotCopilotAPI.Models
{
    public class CopilotEntity
    {
        public string Entity_ID { get; set; } = string.Empty;
        public string Customer_ID { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public DateTimeOffset Created_At { get; set; }
    }
}
