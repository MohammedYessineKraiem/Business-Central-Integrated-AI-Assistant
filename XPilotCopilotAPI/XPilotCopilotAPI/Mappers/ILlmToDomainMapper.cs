using System.Collections.Generic;

namespace XPilotCopilotAPI.Mappers
{
    public interface ILlmToDomainMapper<TDomain>
    {
        /// <summary>
        /// Maps a dictionary of LLM parameters to a strongly typed domain model
        /// </summary>
        /// <returns>Mapped domain model instance</returns>
        TDomain Map(Dictionary<string, object> parameters);
    }
}
