// The chat bar's test page: the cdd-board mod's real hooks module, registered with the stand-in for the Claude app.
import { register } from '../hooks/register'
import { startChat } from './claude-code-stand-in'

void startChat(register as never)
