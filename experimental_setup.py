from copy import deepcopy
from typing import Type, Dict, List, Any, Optional
from functools import partial
from multiprocessing import Pool

from mesa import Model
from mesa.batchrunner import _model_run_func
from tqdm.auto import tqdm

from model import AgentModel



def get_strategies(total_agents=50, env_count=3) -> List[Dict[str, int]]:
    """code starts to test here! this is similar to a strategy dictionary"""
    strats = []

    """setup strategies below"""
    strats.append({"default": 20, "lowtrust": 20, "notrust": 10})
    strats.append({"default": 10, "lowtrust": 20, "notrust": 20})
    strats.append({"default": 10, "lowtrust": 20, "notrust": 20})
    strats.append({"default": 10, "lowtrust": 20, "notrust": 20})
    """"setup strategies above"""
    

    for idx, strat in enumerate(strats):
        if sum(strat.values()) != total_agents:
            raise Exception(
                f"created strat: {sum(strat.values())} does not equal amount of agents in environment: {total_agents}")

    if len(strats) != env_count:
        raise Exception(
            f"amount of created strategies: {len(strats)} does not match with amount of environments: {env_count}")

    return strats

def get_(total_agents=50, env_count=3) -> List[Dict[str, int]]:
    pass


def get_parameters(env_count: int = 4, N=50) -> List[Dict[str, Any]]:
    """method to get the parameters for each environment (mainly hardcoded)"""
    params = []
    strategies = get_strategies(total_agents=N, env_count=env_count)
    standard_dict = {"N": N, "width": 10, "height": 10}
    for idx in range(env_count):
        individual_params = deepcopy(standard_dict)
        individual_params["strategies"] = strategies[idx]
        params.append(individual_params)

    return params


def batch_run(
        model_cls: Type[Model],
        number_processes: Optional[int] = 1,
        iterations: int = 3,
        data_collection_period: int = -1,
        max_steps: int = 1000,
        display_progress: bool = True):
    """method to run multiple environmental setups for final results"""

    runs_list = []
    run_id = 0
    params = get_parameters(iterations)

    for iteration in range(iterations):
        kwargs = params[iteration]
        runs_list.append((run_id, iteration, kwargs))
        run_id += 1

    process_func = partial(
        _model_run_func,
        model_cls,
        max_steps=max_steps,
        data_collection_period=data_collection_period,
    )

    results: List[Dict[str, Any]] = []

    with tqdm(total=len(runs_list), disable=not display_progress) as pbar:
        if number_processes == 1:
            for run in runs_list:
                data = process_func(run)
                results.extend(data)
                pbar.update()
        else:
            with Pool(number_processes) as p:
                for data in p.imap_unordered(process_func, runs_list):
                    results.extend(data)
                    pbar.update()

    return results


def setup_experiment():
    """run batch run and show results"""
    results = batch_run(model_cls=AgentModel,  # mesa model
                        number_processes=4,
                        iterations=4,
                        data_collection_period=-1,
                        max_steps=1000,
                        display_progress=True)

    for result in results:
        print(result)


if __name__ == '__main__':
    setup_experiment()
