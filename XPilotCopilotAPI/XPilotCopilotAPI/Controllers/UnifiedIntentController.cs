using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;
using XPilotCopilotAPI.DTOs;
using XPilotCopilotAPI.Services;

namespace XPilotCopilotAPI.Controllers
{
    [ApiController]
    [Route("copilot")]
    public class UnifiedIntentController : ControllerBase
    {
        private readonly IIntentParserService _intentParserService;
        private readonly ILogger<UnifiedIntentController> _logger;

        public UnifiedIntentController(IIntentParserService intentParserService, ILogger<UnifiedIntentController> logger)
        {
            _intentParserService = intentParserService;
            _logger = logger;
        }

        [HttpPost("unified")]
        public async Task<IActionResult> ClassifyPrompt([FromBody] PromptClassificationRequestDTO request)
        {
            if (string.IsNullOrWhiteSpace(request.Prompt))
                return BadRequest("Prompt cannot be empty.");

            var classificationDto = await _intentParserService.ClassifyPromptAsync(request.Prompt, request.ModelName);

            _logger.LogInformation("Prompt classified as {Type}", classificationDto.Type);

            return Ok(classificationDto);
        }

        [HttpGet("test")]
        public IActionResult Test() => Ok("API is live");
    }
}
