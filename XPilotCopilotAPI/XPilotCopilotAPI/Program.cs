using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using System.IO;
using System.Net.Http;
using XPilotCopilotAPI.DAOs;
using XPilotCopilotAPI.Mappers;
using XPilotCopilotAPI.Models;
using XPilotCopilotAPI.Services;
namespace XPilotCopilotAPI
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            builder.Configuration
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                .AddUserSecrets<Program>()
                .AddEnvironmentVariables();

            // Bind LLMProviders config section correctly
            builder.Services.Configure<LLMSettings>(options =>
            {
                var llmProviders = builder.Configuration.GetSection("LLMProviders").Get<List<LLMProviderConfig>>();
                if (llmProviders != null)
                    options.LLMProviders = llmProviders;
            });


            // DAOs
            builder.Services.AddScoped<ICustomerDao, CustomerDao>();
            builder.Services.AddScoped<ICopilotEntityDao, CopilotEntityDao>();

            //Mappers
            builder.Services.AddSingleton<ILlmToDomainMapper<Customer>, LlmToCustomerMapper>();
            builder.Services.AddSingleton<ILlmToDomainMapper<CopilotEntity>, LlmToCopilotEntityMapper>();

            //services
            builder.Services.AddSingleton<ModelRouter>();
            builder.Services.AddHttpClient<ChatService>(); // HttpClient
            builder.Services.AddScoped<IIntentParserService, IntentParserService>();
            builder.Services.AddScoped<ICommandService, CommandService>();
            builder.Services.AddScoped<ILlmService, LlmService>();

            builder.Services.AddControllers();
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();

            var app = builder.Build();

            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI();
            }

            app.UseHttpsRedirection();
            app.UseAuthorization();
            app.MapControllers();

            app.Run();
        }
    }
}
