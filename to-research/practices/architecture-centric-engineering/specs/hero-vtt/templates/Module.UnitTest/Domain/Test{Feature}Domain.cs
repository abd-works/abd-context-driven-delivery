using FluentAssertions;
using Library.GameCommunicator;
using Library.ProcessCommunicator;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Module.HeroVirtualTabletop.{{Feature}};

namespace Module.UnitTest.Domain
{
    [TestClass]
    public class Test{{Feature}}Domain
    {
        private FakeMemoryInstance _memory = null!;
        private NoOpGameCommandExecutor _executor = null!;
        private {{Domain}} _{{domainField}} = null!;

        [TestInitialize]
        public void Given{{Setup}}()
        {
            _memory = new FakeMemoryInstance();
            _executor = new NoOpGameCommandExecutor();
            _{{domainField}} = new {{Domain}}(_executor, _memory) { Name = "{{ExampleName}}" };
        }

        [TestMethod]
        public void When{{Action}}_Then{{ExpectedOutcome}}()
        {
            _{{domainField}}.{{DomainAction1}}();

            // Assert domain post-state
            _executor.LastCommand.Should().Contain("{{ExampleName}}");
        }
    }
}
