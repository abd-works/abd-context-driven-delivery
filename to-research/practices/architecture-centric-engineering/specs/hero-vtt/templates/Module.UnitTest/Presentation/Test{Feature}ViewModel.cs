using FluentAssertions;
using Library.GameCommunicator;
using Library.ProcessCommunicator;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Module.HeroVirtualTabletop.{{Feature}};

namespace Module.UnitTest.Presentation
{
    [TestClass]
    public class Test{{Feature}}ViewModel
    {
        private FakeMemoryInstance _memory = null!;
        private {{Domain}} _{{domainField}} = null!;
        private {{Feature}}ViewModel _vm = null!;

        [TestInitialize]
        public void GivenAViewModelWiredToAReal{{Domain}}()
        {
            _memory = new FakeMemoryInstance();
            _{{domainField}} = new {{Domain}}(new NoOpGameCommandExecutor(), _memory)
                { Name = "{{ExampleName}}" };
            _vm = new {{Feature}}ViewModel(_{{domainField}});
        }

        [TestMethod]
        public void When{{Command1}}Executed_ThenBindingAndDomainBothUpdate()
        {
            _vm.{{Command1}}.Execute();

            // Assert binding state AND domain post-state
            _vm.{{Domain}}Name.Should().Be("{{ExampleName}}");
        }
    }
}
