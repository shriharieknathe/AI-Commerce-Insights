
from langchain.callbacks.base import BaseCallbackHandler
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, TypeVar, Union
from uuid import UUID
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.documents import Document
import time


from jaeger_client import Config, span, span_context, constants

def init_tracer(service_name):
    config = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'logging': True,
        },
        service_name=service_name,
    )
    return config.initialize_tracer()

tracer = init_tracer('Enzyme')


def llm_trace_to_jaeger(data, span_id, trace_id):
    # trace_id = random.getrandbits(64)
    
    for x in data[::-1]:
        
        if x['parent_run_id'] is not None:
            context = span_context.SpanContext(trace_id = trace_id,span_id = x['run_id'].int & 0xFFFFFFFFFFFFFFFF,parent_id=x['parent_run_id'].int & 0xFFFFFFFFFFFFFFFF,flags = 1)
        else:
            context = span_context.SpanContext(trace_id = trace_id,span_id = x['run_id'].int & 0xFFFFFFFFFFFFFFFF,parent_id=span_id,flags = 1)

        if x["response_metadata"]:
            tag = {
                '1. prompt_tokens': x["response_metadata"]['prompt_tokens'],
                '2. completion_tokens': x["response_metadata"]['completion_tokens'],
                '3. total_tokens': x["response_metadata"]['total_tokens'],
                '4. model_id': x["response_metadata"]['model_id'],
                '5. input': str(x["input"])[:500],
                '6. output': str(x["output"])[:500],
            }
        else:
            tag = {
                '1. input': str(x["input"])[:500],
                '2. output': str(x["output"])[:500],
            }        
        a = span.Span(context=context,tracer=tracer, operation_name=x["chain_name"],tags= tag, start_time=x["start_time"])

        a.finish(finish_time = x['end_time'])

class CallbackHandler(BaseCallbackHandler):

    def __init__(
        self,
    ) -> None:
        self.temp_list = []
        self.result_list = []

    def append_to_list(
        self,
        input: Any,
        output: Any,
        key: str,
        value: Any,
        start_time: Any,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        response_metadata: Optional[Dict] = None,
    ) -> None:
        
        payload = {
            "chain_name": key,
            "latency": value,
            'start_time': start_time,
            'end_time': start_time + value,
            "run_id":run_id,
            "parent_run_id":parent_run_id,
            "input": input,
            "output": output,
            "response_metadata": response_metadata,
        }
        self.result_list.append(payload)


    def infi(self):
        temp_result_list = self.result_list  
        self.result_list = []  
        self.token_usage = []
        # print(1111, temp_result_list)
        return temp_result_list


    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        llm_name = serialized.get("name", serialized.get("id", ["<unknown>"])[-1])
        self.temp_list.append({"time": time.time(), "chain_name": llm_name, "data": prompts })


    def on_llm_end(
        self, 
        response: LLMResult,*,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None, 
        **kwargs: Any,
    ) -> None:
        # Calculate and track the request latency.
        last_dict = self.temp_list[-1]  # Retrieve the last dictionary in the list
        latency = time.time() - last_dict['time']
        self.temp_list.remove(last_dict)
        
        metadata = response.generations[0][0].message.response_metadata
    
        # Handle model_id
        model_id = metadata.get('model_name') or metadata.get('model_id')
        
        # Handle token usage
        token_usage = metadata.get('token_usage') or metadata.get('usage') or metadata.get('usage_metadata')
        if token_usage:
            prompt_tokens = token_usage.get('prompt_tokens', 0) or token_usage.get('prompt_token_count', 0)
            completion_tokens = token_usage.get('completion_tokens', 0) or token_usage.get('candidates_token_count', 0)
            total_tokens = token_usage.get('total_tokens', 0) or token_usage.get('total_token_count', 0)
        else:
            prompt_tokens = completion_tokens = total_tokens = 0
        
        payload = {
            'model_id': model_id,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }
        prompt_response = response.generations[0][0].text
        self.append_to_list(last_dict['data'], prompt_response,last_dict['chain_name'], latency,last_dict['time'],run_id, parent_run_id, payload )


    def on_chain_start(
        self, 
        serialized: Dict[str, Any], 
        inputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None, 
        **kwargs: Any,
    ) -> None:
        """Do nothing when LLM chain starts."""
        chain_name = serialized.get("name", serialized.get("id", ["<unknown>"])[-1])
        self.temp_list.append({"time": time.time(), "chain_name": chain_name , "data": inputs })


    def on_chain_end(
        self, 
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None, 
        **kwargs: Any,
    ) -> None:
        """Do nothing when LLM chain ends."""
        last_dict = self.temp_list[-1]  # Retrieve the last dictionary in the list
        latency = time.time() - last_dict['time']
        self.temp_list.remove(last_dict)
        self.append_to_list(last_dict['data'],outputs,last_dict['chain_name'], latency,last_dict['time'],run_id, parent_run_id  )


    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Do nothing when tool starts."""
        self.temp_list.append({"time": time.time(), "chain_name": "on_tool_start" , "data": input_str })


    def on_tool_end(
        self,
        output: str,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> None:
        """Do nothing when tool ends."""
        
        last_dict = self.temp_list[-1]  # Retrieve the last dictionary in the list
        latency = time.time() - last_dict['time']
        self.temp_list.remove(last_dict)
        self.append_to_list(last_dict['data'],output,last_dict['chain_name'], latency,last_dict['time'],run_id, parent_run_id  )


    def on_retriever_start(
        self,
        serialized: Dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when Retriever starts running."""
        
        self.temp_list.append({"time": time.time(), "chain_name": "VectorStoreRetriever" , "data": [query] })

   
    def on_retriever_end(
        self,
        documents: Sequence[Document],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when Retriever ends running."""
        
        last_dict = self.temp_list[-1]  # Retrieve the last dictionary in the list
        latency = time.time() - last_dict['time']
        self.temp_list.remove(last_dict)
        self.append_to_list(last_dict['data'],None, last_dict['chain_name'], latency,last_dict['time'],run_id, parent_run_id  )

