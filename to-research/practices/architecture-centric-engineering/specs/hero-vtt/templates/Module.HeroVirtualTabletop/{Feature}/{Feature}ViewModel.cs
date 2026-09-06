using Prism.Commands;
using Prism.Mvvm;

namespace Module.HeroVirtualTabletop.{{Feature}}
{
    public class {{Feature}}ViewModel : BindableBase
    {
        private readonly {{Domain}} _{{domainField}};

        public {{Feature}}ViewModel({{Domain}} {{domainField}})
        {
            _{{domainField}} = {{domainField}};
            {{Command1}} = new DelegateCommand(
                () => _{{domainField}}.{{DomainAction1}}());
        }

        public string {{Domain}}Name => _{{domainField}}.Name;

        // Bound properties — direct domain references
        public bool IsSpawned => _{{domainField}}.IsSpawned;

        public DelegateCommand {{Command1}} { get; }
    }
}
