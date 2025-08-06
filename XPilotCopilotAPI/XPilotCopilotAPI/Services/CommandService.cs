using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using XPilotCopilotAPI.DTOs;
using XPilotCopilotAPI.Models;
using XPilotCopilotAPI.DAOs;
using XPilotCopilotAPI.Mappers;

public class CommandService : ICommandService
{
    private readonly ICustomerDao _customerDao;
    private readonly ICopilotEntityDao _copilotEntityDao;
    private readonly ILlmToDomainMapper<Customer> _customerMapper;
    private readonly ILlmToDomainMapper<CopilotEntity> _copilotEntityMapper;
    private readonly ILogger<CommandService> _logger;

    private static readonly HashSet<string> SupportedActions = new(StringComparer.OrdinalIgnoreCase)
    {
        "Create", "Update", "Delete", "Get", "GetAll"
    };

    private static readonly HashSet<string> SupportedEntities = new(StringComparer.OrdinalIgnoreCase)
    {
        "Customer", "CopilotEntity"
    };

    public CommandService(
        ICustomerDao customerDao,
        ICopilotEntityDao copilotEntityDao,
        ILlmToDomainMapper<Customer> customerMapper,
        ILlmToDomainMapper<CopilotEntity> copilotEntityMapper,
        ILogger<CommandService> logger)
    {
        _customerDao = customerDao;
        _copilotEntityDao = copilotEntityDao;
        _customerMapper = customerMapper;
        _copilotEntityMapper = copilotEntityMapper;
        _logger = logger;
    }

    public async Task<CommandResponseDTO> ExecuteCommandAsync(CommandParsedDTO command)
    {
        try
        {
            var validation = ValidateCommand(command);
            if (!validation.IsValid)
            {
                _logger.LogWarning("Validation failed: {Reason}", validation.ErrorMessage);
                return new CommandResponseDTO { Success = false, Message = validation.ErrorMessage };
            }

            var action = command.Action.Trim();
            var entity = command.Entity.Trim();

            _logger.LogInformation("Executing {Action} on {Entity}", action, entity);

            return entity.Equals("Customer", StringComparison.OrdinalIgnoreCase)
                ? await ExecuteCustomerCommandAsync(action, command.Parameters)
                : await ExecuteCopilotEntityCommandAsync(action, command.Parameters);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "ExecuteCommandAsync failed");
            return new CommandResponseDTO { Success = false, Message = $"Internal error: {ex.Message}" };
        }
    }

    /// <summary>
    /// Safely extracts a string value from a parameter that could be a JsonElement, string, number, etc.
    /// </summary>
    private string? ExtractStringValue(object parameter, string parameterName)
    {
        if (parameter == null)
        {
            _logger.LogWarning("Parameter {ParameterName} is null", parameterName);
            return null;
        }

        _logger.LogDebug("Extracting {ParameterName}: {Value} (Type: {Type})",
            parameterName, parameter, parameter.GetType().Name);

        try
        {
            return parameter switch
            {
                string str => string.IsNullOrWhiteSpace(str) ? null : str.Trim(),
                JsonElement jsonElement => ExtractFromJsonElement(jsonElement, parameterName),
                int intVal => intVal.ToString(),
                long longVal => longVal.ToString(),
                decimal decVal => decVal.ToString("0"),
                double doubleVal => doubleVal.ToString("0"),
                float floatVal => floatVal.ToString("0"),
                _ => parameter.ToString()?.Trim()
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to extract string value from parameter {ParameterName}", parameterName);
            return null;
        }
    }

    /// <summary>
    /// Extracts string value from JsonElement handling different value types
    /// </summary>
    private string? ExtractFromJsonElement(JsonElement element, string parameterName)
    {
        try
        {
            var result = element.ValueKind switch
            {
                JsonValueKind.String => element.GetString(),
                JsonValueKind.Number when element.TryGetInt64(out var longVal) => longVal.ToString(),
                JsonValueKind.Number when element.TryGetDecimal(out var decVal) => decVal.ToString("0"),
                JsonValueKind.Number => element.GetRawText(),
                JsonValueKind.True => "true",
                JsonValueKind.False => "false",
                JsonValueKind.Null => null,
                _ => element.GetRawText()
            };

            _logger.LogDebug("Extracted from JsonElement {ParameterName}: '{Value}' (ValueKind: {ValueKind})",
                parameterName, result, element.ValueKind);

            return string.IsNullOrWhiteSpace(result) ? null : result.Trim();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to extract from JsonElement {ParameterName} (ValueKind: {ValueKind})",
                parameterName, element.ValueKind);
            return null;
        }
    }

    private (bool IsValid, string ErrorMessage) ValidateCommand(CommandParsedDTO command)
    {
        if (command == null) return (false, "Command cannot be null");
        if (string.IsNullOrWhiteSpace(command.Action)) return (false, "Action is required");
        if (string.IsNullOrWhiteSpace(command.Entity)) return (false, "Entity is required");

        if (!SupportedActions.Contains(command.Action))
            return (false, $"Unsupported action '{command.Action}'");

        if (!SupportedEntities.Contains(command.Entity))
            return (false, $"Unsupported entity '{command.Entity}'");

        if (command.Action.Equals("Update", StringComparison.OrdinalIgnoreCase) ||
            command.Action.Equals("Delete", StringComparison.OrdinalIgnoreCase) ||
            command.Action.Equals("Get", StringComparison.OrdinalIgnoreCase))
        {
            var requiredId = command.Entity.Equals("Customer", StringComparison.OrdinalIgnoreCase) ? "Customer_ID" : "Entity_ID";

            if (!command.Parameters.TryGetValue(requiredId, out var idVal))
                return (false, $"'{requiredId}' parameter is missing for {command.Action} on {command.Entity}");

            var extractedId = ExtractStringValue(idVal, requiredId);
            if (string.IsNullOrWhiteSpace(extractedId))
                return (false, $"'{requiredId}' must have a valid value for {command.Action} on {command.Entity}");
        }

        return (true, "");
    }

    // ----------------- CUSTOMER -----------------

    private async Task<CommandResponseDTO> ExecuteCustomerCommandAsync(string action, Dictionary<string, object> parameters)
    {
        try
        {
            switch (action.ToLowerInvariant())
            {
                case "create":
                    var newCustomer = _customerMapper.Map(parameters);
                    return await _customerDao.CreateAsync(newCustomer);

                case "update":
                    var updateCustomer = _customerMapper.Map(parameters);
                    return await _customerDao.UpdateAsync(updateCustomer);

                case "delete":
                    var deleteId = ExtractStringValue(parameters["Customer_ID"], "Customer_ID");
                    if (deleteId == null)
                        return new CommandResponseDTO { Success = false, Message = "Invalid Customer_ID for delete operation" };

                    _logger.LogInformation("Deleting customer with ID: '{CustomerId}'", deleteId);
                    return await _customerDao.DeleteAsync(deleteId);

                case "get":
                    var getId = ExtractStringValue(parameters["Customer_ID"], "Customer_ID");
                    if (getId == null)
                        return new CommandResponseDTO { Success = false, Message = "Invalid Customer_ID for get operation" };

                    _logger.LogInformation("Getting customer with ID: '{CustomerId}' (Length: {Length})", getId, getId.Length);
                    return await _customerDao.GetAsync(getId);

                case "getall":
                    return await _customerDao.GetAllAsync();

                default:
                    return new CommandResponseDTO { Success = false, Message = $"Unsupported customer action: {action}" };
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing Customer command '{Action}'", action);
            return new CommandResponseDTO { Success = false, Message = $"Error: {ex.Message}" };
        }
    }

    // ----------------- COPILOT ENTITY -----------------

    private async Task<CommandResponseDTO> ExecuteCopilotEntityCommandAsync(string action, Dictionary<string, object> parameters)
    {
        try
        {
            switch (action.ToLowerInvariant())
            {
                case "create":
                    var newEntity = _copilotEntityMapper.Map(parameters);
                    return await _copilotEntityDao.CreateAsync(newEntity);

                case "update":
                    var updateEntity = _copilotEntityMapper.Map(parameters);
                    return await _copilotEntityDao.UpdateAsync(updateEntity);

                case "delete":
                    var deleteId = ExtractStringValue(parameters["Entity_ID"], "Entity_ID");
                    if (deleteId == null)
                        return new CommandResponseDTO { Success = false, Message = "Invalid Entity_ID for delete operation" };

                    _logger.LogInformation("Deleting CopilotEntity with ID: '{EntityId}'", deleteId);
                    return await _copilotEntityDao.DeleteAsync(deleteId);

                case "get":
                    var getId = ExtractStringValue(parameters["Entity_ID"], "Entity_ID");
                    if (getId == null)
                        return new CommandResponseDTO { Success = false, Message = "Invalid Entity_ID for get operation" };

                    _logger.LogInformation("Getting CopilotEntity with ID: '{EntityId}' (Length: {Length})", getId, getId.Length);
                    return await _copilotEntityDao.GetAsync(getId);

                case "getall":
                    return await _copilotEntityDao.GetAllAsync();

                default:
                    return new CommandResponseDTO { Success = false, Message = $"Unsupported CopilotEntity action: {action}" };
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing CopilotEntity command '{Action}'", action);
            return new CommandResponseDTO { Success = false, Message = $"Error: {ex.Message}" };
        }
    }

}