using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
using XPilotCopilotAPI.DTOs;
// Namespace example, adjust to your project structure
namespace XPilotCopilotAPI.Controllers
{
    // This controller handles requests for natural language commands parsed by LLM
    [ApiController]
    [Route("copilot")]
    public class CopilotCommandController : ControllerBase
    {
        private readonly ILlmService _llmService;
        private readonly ICommandService _commandService;
        private readonly ILogger<CopilotCommandController> _logger;

        // Dependency injection of services and logger
        public CopilotCommandController(ILlmService llmService, ICommandService commandService, ILogger<CopilotCommandController> logger)
        {
            _llmService = llmService;
            _commandService = commandService;
            _logger = logger;
        }

        // POST /copilot/command
        // Receives natural language prompt + model info, returns execution result
        [HttpPost("command")]
        public async Task<IActionResult> ExecuteCommand([FromBody] CommandRequestDTO request)
        {
            // Validate inputs
            if (string.IsNullOrWhiteSpace(request.Prompt))
                return BadRequest("Prompt cannot be empty.");

            if (string.IsNullOrWhiteSpace(request.Model))
                return BadRequest("Model must be specified.");

            try
            {
                _logger.LogInformation("Received prompt: {Prompt} with model: {Model}", request.Prompt, request.Model);

                // Call LLM service to parse natural language prompt into structured command
                CommandParsedDTO parsedCommand = await _llmService.ParseCommandAsync(request.Prompt, request.Model);

                if (parsedCommand == null)
                {
                    _logger.LogWarning("LLM returned null or invalid parsed command.");
                    return BadRequest("Failed to parse command.");
                }

                _logger.LogInformation("Parsed command action: {Action}", parsedCommand.Action);

                CommandResponseDTO commandResult = await _commandService.ExecuteCommandAsync(parsedCommand);
                _logger.LogInformation("Returning CommandResponseDTO: {@Result}", commandResult.Message);
                return Ok(commandResult);


                
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error occurred while executing command.");
                // Return generic 500 error without exposing internal details
                

                return StatusCode(500, new CommandResponseDTO
                {
                    Success = false,
                    Message = "Internal server error while processing the command.",
                    Data = null
                });
            }
        }
    }
}
