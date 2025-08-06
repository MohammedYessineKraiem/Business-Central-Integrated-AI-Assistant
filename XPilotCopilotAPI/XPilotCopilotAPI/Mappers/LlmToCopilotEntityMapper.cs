using System;
using System.Collections.Generic;
using XPilotCopilotAPI.Models;

namespace XPilotCopilotAPI.Mappers
{
    public class LlmToCopilotEntityMapper : ILlmToDomainMapper<CopilotEntity>
    {
        public CopilotEntity Map(Dictionary<string, object> parameters)
        {
            var entity = new CopilotEntity();

            Console.WriteLine("---- MAPPING CopilotEntity ----");

            foreach (var kv in parameters)
            {
                Console.WriteLine($"Key: {kv.Key}, Value: {kv.Value}");
            }

            if (parameters.TryGetValue("Entity_ID", out var idObj))
            {
                entity.Entity_ID = idObj?.ToString() ?? string.Empty;
            }

            if (parameters.TryGetValue("Customer_ID", out var customerIdObj))
            {
                entity.Customer_ID = customerIdObj?.ToString() ?? string.Empty;
            }

            if (parameters.TryGetValue("Title", out var titleObj))
            {
                entity.Title = titleObj?.ToString() ?? string.Empty;
            }

            if (parameters.TryGetValue("Description", out var descObj))
            {
                entity.Description = descObj?.ToString()    ?? string.Empty;
            }

            if (parameters.TryGetValue("Status", out var statusObj))
            {
                entity.Status = statusObj?.ToString() ?? string.Empty;
            }
            if (parameters.TryGetValue("Created_At", out var createdObj))
            {
                if (createdObj is DateTimeOffset dto)
                    entity.Created_At = dto;
                else if (DateTimeOffset.TryParse(createdObj.ToString(), out var parsedDto))
                    entity.Created_At = parsedDto;
            }


            return entity;
        }
    }
}
