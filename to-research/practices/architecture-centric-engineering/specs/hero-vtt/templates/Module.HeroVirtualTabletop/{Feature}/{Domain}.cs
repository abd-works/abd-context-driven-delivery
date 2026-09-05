using System.ComponentModel;
using System.Runtime.CompilerServices;
using Library.GameCommunicator;
using Library.ProcessCommunicator;

namespace Module.HeroVirtualTabletop.{{Feature}}
{
    public class {{Domain}} : INotifyPropertyChanged
    {
        private readonly IGameCommandExecutor _executor;
        private readonly IMemoryInstance _memory;

        public {{Domain}}(IGameCommandExecutor executor, IMemoryInstance memory)
        {
            _executor = executor;
            _memory = memory;
        }

        public string Name { get; set; } = string.Empty;

        private bool _isSpawned;
        public bool IsSpawned
        {
            get => _isSpawned;
            private set { _isSpawned = value; OnPropertyChanged(); }
        }

        // Domain methods — replace with real business operations
        public void {{DomainAction1}}()
        {
            _executor.ExecuteCmd($"{{commandVerb}} {Name}");
            // _memory.SetPosition / SetFacing / ReadXYZ as needed
        }

        public event PropertyChangedEventHandler? PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string? n = null) =>
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(n));
    }
}
