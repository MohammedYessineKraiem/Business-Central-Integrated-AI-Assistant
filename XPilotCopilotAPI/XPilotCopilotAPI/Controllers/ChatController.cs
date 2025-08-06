using Microsoft.AspNetCore.Mvc;
using XPilotCopilotAPI.DTOs;
using XPilotCopilotAPI.Services;
using System.Threading.Tasks;

namespace XPilotCopilotAPI.Controllers
{
    [ApiController]
    [Route("copilot/chat")]
    public class ChatController : ControllerBase
    {
        private readonly ChatService _chatService;

        public ChatController(ChatService chatService)
        {
            _chatService = chatService;
        }

        [HttpPost]
        public async Task<IActionResult> Chat([FromBody] PromptRequestDTO prompt)
        {
            var response = await _chatService.GetChatResponseAsync(prompt);
            return Ok(response);
        }
    }
}
