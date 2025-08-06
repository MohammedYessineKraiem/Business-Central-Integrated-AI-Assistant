namespace XPilotCopilotAPI.Models
{
    public class Customer
    {
        public string Customer_ID { get; set; } = string.Empty;
        public string Full_Name { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Phone_Number { get; set; } = string.Empty;
        public DateTimeOffset  Created_At { get; set; }
    }
}
