using XPilotCopilotAPI.Models;

public interface ICustomerDao
{
    Task<CommandResponseDTO> CreateAsync(Customer customer);
    Task<CommandResponseDTO> UpdateAsync(Customer customer);
    Task<CommandResponseDTO> DeleteAsync(string customerId);
    Task<CommandResponseDTO> GetAsync(string customerId);

    Task<CommandResponseDTO> GetAllAsync();

}
