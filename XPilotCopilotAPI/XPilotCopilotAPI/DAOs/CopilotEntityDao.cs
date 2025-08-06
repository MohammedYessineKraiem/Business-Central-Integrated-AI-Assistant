using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using XPilotCopilotAPI.DTOs;
using XPilotCopilotAPI.Models;

namespace XPilotCopilotAPI.DAOs
{
    public class CopilotEntityDao : ICopilotEntityDao
    {
        private readonly ILogger<CopilotEntityDao> _logger;
        private readonly IConfiguration _configuration;

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        private string BaseUrl => _configuration["OData:CopilotEntityUrl"]
            ?? throw new InvalidOperationException("OData:CopilotEntityUrl configuration is missing");

        private string BaseurlFull => _configuration["OData:CopilotEntityUrlFull"]
            ?? throw new InvalidOperationException("Missing config: OData:CopilotEntityUrlFull");

        private string Username => _configuration["OData:Username"]
            ?? throw new InvalidOperationException("OData:Username configuration is missing");

        private string Password => _configuration["OData:Password"]
            ?? throw new InvalidOperationException("OData:Password configuration is missing");

        public CopilotEntityDao(IConfiguration configuration, ILogger<CopilotEntityDao> logger)
        {
            _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));

            _logger.LogInformation("CopilotEntityDao initialized. Base URL: {BaseUrl}", BaseUrl);
        }

        private HttpClient CreateHttpClient()
        {
            var handler = new HttpClientHandler
            {
                Credentials = new NetworkCredential(Username, Password),
                PreAuthenticate = true
            };

            var client = new HttpClient(handler)
            {
                BaseAddress = new Uri(BaseUrl)
            };

            client.DefaultRequestHeaders.Accept.Clear();
            client.DefaultRequestHeaders.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("application/json"));
            client.DefaultRequestHeaders.UserAgent.ParseAdd("XPilotCopilot/1.0");

            return client;
        }

        private HttpClient CreateHttpClient2()
        {
            var handler = new HttpClientHandler
            {
                Credentials = new NetworkCredential(Username, Password),
                PreAuthenticate = true
            };

            var client = new HttpClient(handler)
            {
                BaseAddress = new Uri(BaseurlFull)
            };
            _logger.LogInformation("HttpClient BaseAddress set to: {BaseAddress}", client.BaseAddress);
            client.DefaultRequestHeaders.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("application/json"));
            client.DefaultRequestHeaders.UserAgent.ParseAdd("XPilotCopilot/1.0");

            return client;
        }
        private static string BuildODataUrl(string id) => $"CopilotEntityOData(Entity_ID='{Uri.EscapeDataString(id)}')";

        public async Task<CommandResponseDTO> CreateAsync(CopilotEntity entity)
        {
            if (entity == null)
                return Fail("Create", "Entity object cannot be null.");

            using var client = CreateHttpClient2();

            try
            {
                var json = JsonSerializer.Serialize(entity, JsonOptions);
                var response = await client.PostAsync("", new StringContent(json, Encoding.UTF8, "application/json"));
                var content = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                    return Fail("Create", $"Status: {response.StatusCode}, Content: {content}");

                var created = JsonSerializer.Deserialize<CopilotEntity>(content, JsonOptions);

                return Success("Create", "Entity created successfully.", created);
            }
            catch (Exception ex)
            {
                return Fail("Create", ex);
            }
        }

        public async Task<CommandResponseDTO> GetAsync(string entityId)
        {
            if (string.IsNullOrWhiteSpace(entityId))
                return Fail("Get", "Entity_ID is required.");

            using var client = CreateHttpClient();

            try
            {
                var url = BuildODataUrl(entityId);
                var response = await client.GetAsync(url);
                var content = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                    return Fail("Get", $"Status: {response.StatusCode}, Content: {content}");

                var entity = JsonSerializer.Deserialize<CopilotEntity>(content, JsonOptions);
                return Success("Get", "Entity retrieved successfully.", entity);
            }
            catch (Exception ex)
            {
                return Fail("Get", ex);
            }
        }


        public async Task<CommandResponseDTO> GetAllAsync()
        {
            using var client = CreateHttpClient2();

            try
            {
                var response = await client.GetAsync("");
                var content = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                    return Fail("GetAll", $"Status: {response.StatusCode}, Content: {content}");

                var wrapper = JsonSerializer.Deserialize<ODataResponseWrapper<CopilotEntity>>(content, JsonOptions);
                return Success("GetAll", "Entities retrieved successfully.", wrapper?.Value ?? new List<CopilotEntity>());
            }
            catch (Exception ex)
            {
                return Fail("GetAll", ex);
            }
        }

        public async Task<CommandResponseDTO> UpdateAsync(CopilotEntity entity)
        {
            if (entity == null || string.IsNullOrWhiteSpace(entity.Entity_ID))
                return Fail("Update", "Entity_ID is required.");

            using var client = CreateHttpClient();

            try
            {
                var url = BuildODataUrl(entity.Entity_ID);

                // Step 1: GET the entity to retrieve the ETag
                var getResponse = await client.GetAsync(url);
                if (!getResponse.IsSuccessStatusCode)
                {
                    var err = await getResponse.Content.ReadAsStringAsync();
                    return Fail("Update", $"Failed to retrieve entity. Status: {getResponse.StatusCode}, Content: {err}");
                }

                var getContent = await getResponse.Content.ReadAsStringAsync();
                using var doc = JsonDocument.Parse(getContent);
                if (!doc.RootElement.TryGetProperty("@odata.etag", out var etagProp))
                    return Fail("Update", "ETag not found in response.");

                var etag = etagProp.GetString();

                // Step 2: PATCH with If-Match header using the ETag
                var json = JsonSerializer.Serialize(entity, JsonOptions);
                var patchRequest = new HttpRequestMessage(new HttpMethod("PATCH"), url)
                {
                    Content = new StringContent(json, Encoding.UTF8, "application/json")
                };
                patchRequest.Headers.IfMatch.ParseAdd(etag);

                var patchResponse = await client.SendAsync(patchRequest);
                var patchContent = await patchResponse.Content.ReadAsStringAsync();

                if (!patchResponse.IsSuccessStatusCode)
                    return Fail("Update", $"Status: {patchResponse.StatusCode}, Content: {patchContent}");

                return Success("Update", "Entity updated successfully.", entity);
            }
            catch (Exception ex)
            {
                return Fail("Update", ex);
            }
        }



        public async Task<CommandResponseDTO> DeleteAsync(string entityId)
        {
            if (string.IsNullOrWhiteSpace(entityId))
                return Fail("Delete", "Entity_ID is required.");

            using var client = CreateHttpClient();

            try
            {
                var url = BuildODataUrl(entityId);
                var response = await client.DeleteAsync(url);
                var content = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                    return Fail("Delete", $"Status: {response.StatusCode}, Content: {content}");

                return Success("Delete", "Entity deleted successfully.", new { DeletedId = entityId });
            }
            catch (Exception ex)
            {
                return Fail("Delete", ex);
            }
        }


        // Shared Response Builders
        private CommandResponseDTO Success(string operation, string message, object? data) =>
            new()
            {
                Success = true,
                Message = $"{operation}: {message}",
                Data = data
            };

        private CommandResponseDTO Fail(string operation, string reason) =>
            new()
            {
                Success = false,
                Message = $"{operation} failed: {reason}",
                Data = null
            };

        private CommandResponseDTO Fail(string operation, Exception ex)
        {
            _logger.LogError(ex, $"{operation} failed with exception");
            return Fail(operation, ex.Message);
        }

        private class ODataResponseWrapper<T>
        {
            public List<T> Value { get; set; } = new();
        }
    }
}
