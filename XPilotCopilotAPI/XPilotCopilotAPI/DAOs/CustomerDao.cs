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
    public class CustomerDao : ICustomerDao
    {
        private readonly ILogger<CustomerDao> _logger;
        private readonly IConfiguration _configuration;

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };

        private string BaseUrl => _configuration["OData:CustomerUrl"]
            ?? throw new InvalidOperationException("Missing config: OData:CustomerUrl");

        private string BaseurlFull => _configuration["OData:CustomerUrlFull"]
            ?? throw new InvalidOperationException("Missing config: OData:CustomerUrlFull");

        private string Username => _configuration["OData:Username"]
            ?? throw new InvalidOperationException("Missing config: OData:Username");

        private string Password => _configuration["OData:Password"]
            ?? throw new InvalidOperationException("Missing config: OData:Password");

        public CustomerDao(IConfiguration configuration, ILogger<CustomerDao> logger)
        {
            _configuration = configuration ?? throw new ArgumentNullException(nameof(configuration));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            var configUrl = _configuration["OData:CustomerUrl"];
            _logger.LogInformation("CustomerDao initialized with base URL: {BaseUrl}", BaseUrl);
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
            _logger.LogInformation("HttpClient BaseAddress set to: {BaseAddress}", client.BaseAddress);
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

        private static string BuildODataUrl(string id) => $"CustomerOdata(Customer_ID='{Uri.EscapeDataString(id)}')";



        public async Task<CommandResponseDTO> CreateAsync(Customer customer)
        {
            if (customer == null) return Error("Customer cannot be null");

            using var client = CreateHttpClient2();
            var payload = JsonSerializer.Serialize(customer, JsonOptions);

            try
            {
                var content = new StringContent(payload, Encoding.UTF8, "application/json");
                _logger.LogDebug("Creating customer with payload: {Payload}", payload);

                var response = await client.PostAsync("", content);
                var responseContent = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var created = DeserializeOrFallback(responseContent, customer);
                    _logger.LogInformation("Customer created: {CustomerId}", customer.Customer_ID);
                    return Success("Customer created successfully", created);
                }

                return HandleHttpError("Create", response.StatusCode, responseContent);
            }
            catch (Exception ex)
            {
                LogAndFail(ex, "customer creation");
                return new CommandResponseDTO { Success = false, Message = "Error during customer creation." };
            }
        }

        public async Task<CommandResponseDTO> UpdateAsync(Customer customer)
        {
            if (customer == null || string.IsNullOrWhiteSpace(customer.Customer_ID))
                return Error("Valid Customer_ID is required for update");

            using var client = CreateHttpClient();
            var url = BuildODataUrl(customer.Customer_ID);
            var json = JsonSerializer.Serialize(customer, JsonOptions);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            try
            {
                // Step 1: Fetch ETag
                var getResponse = await client.GetAsync(url);
                if (!getResponse.IsSuccessStatusCode)
                {
                    var getError = await getResponse.Content.ReadAsStringAsync();
                    return HandleHttpError("Fetch ETag for update", getResponse.StatusCode, getError);
                }

                var eTag = getResponse.Headers.ETag?.Tag ?? "*"; // Use "*" fallback if needed

                // Step 2: PATCH with ETag
                _logger.LogDebug("Updating customer at {Url} with ETag {ETag}", url, eTag);
                var request = new HttpRequestMessage(HttpMethod.Patch, url)
                {
                    Content = content
                };
                request.Headers.IfMatch.ParseAdd(eTag);

                var patchResponse = await client.SendAsync(request);
                var patchContent = await patchResponse.Content.ReadAsStringAsync();

                if (patchResponse.IsSuccessStatusCode)
                {
                    _logger.LogInformation("Customer updated: {CustomerId}", customer.Customer_ID);
                    return Success("Customer updated successfully", customer);
                }

                return HandleHttpError("Update", patchResponse.StatusCode, patchContent);
            }
            catch (Exception ex)
            {
                LogAndFail(ex, "customer update");
                return new CommandResponseDTO { Success = false, Message = "Error during customer update." };
            }
        }


        public async Task<CommandResponseDTO> DeleteAsync(string customerId)
        {
            if (string.IsNullOrWhiteSpace(customerId))
                return Error("Customer_ID is required for delete");

            using var client = CreateHttpClient();
            var url = BuildODataUrl(customerId);

            try
            {
                _logger.LogDebug("Deleting customer at {Url}", url);
                var response = await client.DeleteAsync(url);
                var responseContent = await response.Content.ReadAsStringAsync();
                _logger.LogInformation($"Calling OData URL: {url} with ID: {customerId}");



                if (response.IsSuccessStatusCode)
                {
                    _logger.LogInformation("Customer deleted: {CustomerId}", customerId);
                    return Success("Customer deleted", new { DeletedId = customerId });
                }

                return HandleHttpError("Delete", response.StatusCode, responseContent);
            }

            catch (Exception ex)
            {
                LogAndFail(ex, "customer deletion");
                return new CommandResponseDTO { Success = false, Message = "Error during customer deletion." };
            }
        }

        public async Task<CommandResponseDTO> GetAsync(string customerId)
        {
            if (string.IsNullOrWhiteSpace(customerId))
                return Error("Customer_ID is required for get");

            using var client = CreateHttpClient();
            var url = BuildODataUrl(customerId);

            try

            {
                _logger.LogDebug("Getting customer from {Url}", url);
                _logger.LogInformation("Calling OData URL: {Url} with ID: {ID}", url, customerId);
                var fullUrl = new Uri(client.BaseAddress, url).ToString();
                _logger.LogInformation("Complete URL being called: {FullUrl}", fullUrl);

                var response = await client.GetAsync(url);
                var responseContent = await response.Content.ReadAsStringAsync();
                _logger.LogInformation($"Calling OData URL: {url} with ID: {customerId}");
                _logger.LogDebug($"Raw Customer_ID: '{customerId}' Length: {customerId.Length}");



                if (response.IsSuccessStatusCode)
                {
                    var customer = JsonSerializer.Deserialize<Customer>(responseContent, JsonOptions);
                    return Success("Customer retrieved", customer);
                }

                return response.StatusCode == HttpStatusCode.NotFound
                    ? Error($"Customer '{customerId}' not found")
                    : HandleHttpError("Get", response.StatusCode, responseContent);
            }
            catch (Exception ex)
            {
                LogAndFail(ex, "customer retrieval");
                return new CommandResponseDTO { Success = false, Message = "Error during customer retrieval." };
            }
        }

        public async Task<CommandResponseDTO> GetAllAsync()
        {
            using var client = CreateHttpClient2();

            try
            {
                _logger.LogDebug("Getting all customers");
                var response = await client.GetAsync("");
                var responseContent = await response.Content.ReadAsStringAsync();

                if (response.IsSuccessStatusCode)
                {
                    var customers = ParseCustomerList(responseContent);
                    return Success($"Retrieved {customers.Count} customers", customers);
                }

                return HandleHttpError("GetAll", response.StatusCode, responseContent);
            }
            catch (Exception ex)
            {
                LogAndFail(ex, "customer list retrieval");
                return new CommandResponseDTO { Success = false, Message = "Error during customer list retrieval." };
            }
        }

        // ---------- Helpers ----------

        private List<Customer> ParseCustomerList(string content)
        {
            try
            {
                var odata = JsonSerializer.Deserialize<ODataResponse<Customer>>(content, JsonOptions);
                return odata?.Value ?? new();
            }
            catch
            {
                return JsonSerializer.Deserialize<List<Customer>>(content, JsonOptions) ?? new();
            }
        }

        private Customer DeserializeOrFallback(string content, Customer fallback)
        {
            try
            {
                return JsonSerializer.Deserialize<Customer>(content, JsonOptions) ?? fallback;
            }
            catch
            {
                return fallback;
            }
        }

        private CommandResponseDTO HandleHttpError(string op, HttpStatusCode status, string body)
        {
            _logger.LogError("{Op} failed: {Status} - {Body}", op, status, body);
            var message = status switch
            {
                HttpStatusCode.BadRequest => "Bad request",
                HttpStatusCode.Unauthorized => "Unauthorized",
                HttpStatusCode.Forbidden => "Forbidden",
                HttpStatusCode.NotFound => "Not found",
                HttpStatusCode.Conflict => "Conflict",
                HttpStatusCode.InternalServerError => "Server error",
                _ => $"HTTP {status}"
            };
            return Error($"{op} failed: {message}");
        }

        private CommandResponseDTO LogAndFail(Exception ex, string op)
        {
            _logger.LogError(ex, "Exception during {Op}", op);
            return Error($"Unexpected error during {op}: {ex.Message}");
        }

        private static CommandResponseDTO Success(string msg, object data) => new()
        {
            Success = true,
            Message = msg,
            Data = data
        };

        private static CommandResponseDTO Error(string msg) => new()
        {
            Success = false,
            Message = msg,
            Data = null
        };

        private class ODataResponse<T>
        {
            public List<T>? Value { get; set; }
        }
    }
}
