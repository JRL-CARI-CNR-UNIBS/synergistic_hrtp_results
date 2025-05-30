#! /usr/bin/env python3

class StatisticalPipeline:

    @staticmethod
    def recipes_duration_pipeline() -> list:
        return [
            {
                '$group': {
                    '_id': '$recipe',
                    'recipe_start': {
                        '$min': '$t_start'
                    },
                    'recipe_end': {
                        '$max': '$t_end'
                    }
                }
            }, {
                '$addFields': {
                    'recipe_duration': {
                        '$subtract': [
                            '$recipe_end', '$recipe_start'
                        ]
                    }
                }
            }, {
                '$project': {
                    '_id': False,
                    'recipe_name': '$_id',
                    'recipe_start': True,
                    'recipe_end': True,
                    'recipe_duration': True
                }
            }
        ]   
    
    @staticmethod
    def grouped_synergies_pipeline() -> list:
        pipeline = [        # Pipeline to group/separate synergies elements by agent  
        {
            '$sort': {
                'agent_skill': 1, 
                'concurrent_skill': 1
            }
        }, {
            '$group': {
                '_id': '$agent', 
                'grouped_task_agent': {
                    '$push': '$$ROOT'
                }
            }
        }
        ]
        return pipeline
