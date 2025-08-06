using System;
using System.Collections.Generic;
using XPilotCopilotAPI.Models;

namespace XPilotCopilotAPI.Mappers
{
    public class LlmToCustomerMapper : ILlmToDomainMapper<Customer>
    {
        public Customer Map(Dictionary<string, object> parameters)
        {
            var customer = new Customer();
            foreach (var kv in parameters)
            {
                Console.WriteLine($"Key: {kv.Key}, Value: {kv.Value}");
            }


            if (parameters.TryGetValue("Customer_ID", out var idObj))
            {
                customer.Customer_ID = idObj?.ToString() ?? string.Empty;
            }

            if (parameters.TryGetValue("Full_Name", out var fullName))
                customer.Full_Name = fullName?.ToString() ?? string.Empty;

            if (parameters.TryGetValue("Username", out var username))
                customer.Username = username?.ToString() ?? string.Empty;

            if (parameters.TryGetValue("Email", out var email))
                customer.Email = email?.ToString() ?? string.Empty;

            if (parameters.TryGetValue("Phone_Number", out var phoneNumber))
                customer.Phone_Number = phoneNumber?.ToString() ?? string.Empty;

            if (parameters.TryGetValue("Created_At", out var createdObj))
            {
                if (createdObj is DateTimeOffset dto)
                    customer.Created_At = dto;
                else if (DateTimeOffset.TryParse(createdObj.ToString(), out var parsedDto))
                    customer.Created_At = parsedDto;
            }

            return customer;
        }
    }
}
