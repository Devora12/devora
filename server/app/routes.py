from flask import jsonify, request
from database import get_collection
from datetime import datetime

def register_routes(app):
    
    # Health check
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})
    
    # Get all projects
    @app.route('/api/projects')
    def get_projects():
        try:
            projects = list(get_collection('projects').find({}, {'_id': 0}))
            return jsonify(projects)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Get project authors
    @app.route('/api/project/<int:project_id>/authors')
    def get_project_authors(project_id):
        try:
            collection = get_collection()
            pipeline = [
                {'$match': {'project_id': project_id}},
                {'$group': {'_id': '$author'}},
                {'$project': {'author': '$_id', '_id': 0}}
            ]
            
            result = list(collection.aggregate(pipeline))
            authors = [item['author'] for item in result if item['author']]
            return jsonify(authors)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Get testcases by author
    @app.route('/api/project/<int:project_id>/testcases-by-author')
    def get_testcases_by_author(project_id):
        try:
            collection = get_collection()
            pipeline = [
                {'$match': {'project_id': project_id}},
                {'$group': {
                    '_id': '$author',
                    'testcases': {'$push': '$testcases'},
                    'count': {'$sum': {'$size': '$testcases'}}
                }},
                {'$project': {
                    'author': '$_id',
                    'testcases': 1,
                    'count': 1,
                    '_id': 0
                }}
            ]
            
            result = list(collection.aggregate(pipeline))
            
            # Flatten testcases and remove duplicates
            for item in result:
                flattened = []
                for tc_list in item['testcases']:
                    flattened.extend(tc_list)
                item['testcases'] = list(set(flattened))
            
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Get commit timeline
    @app.route('/api/project/<int:project_id>/commit-timeline')
    def get_commit_timeline(project_id):
        try:
            collection = get_collection()
            pipeline = [
                {'$match': {'project_id': project_id}},
                {'$project': {
                    'author': 1,
                    'last_commit_date': 1,
                    'commit_count': 1
                }},
                {'$sort': {'last_commit_date': 1}}
            ]
            
            records = list(collection.aggregate(pipeline))
            timeline_data = []
            
            for record in records:
                author = record.get('author')
                commit_date = record.get('last_commit_date')
                commit_count = record.get('commit_count', 0)
                
                if author and commit_date:
                    timeline_data.append({
                        'date': commit_date,
                        'author': author,
                        'commits': commit_count
                    })
            
            return jsonify(timeline_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Get author testcases
    @app.route('/api/author/<author>/testcases')
    def get_author_testcases(author):
        try:
            collection = get_collection()
            pipeline = [
                {'$match': {'author': author}},
                {'$project': {'testcases': 1, '_id': 0}}
            ]
            
            result = list(collection.aggregate(pipeline))
            
            # Flatten testcases
            all_testcases = []
            for item in result:
                if 'testcases' in item and item['testcases']:
                    all_testcases.extend(item['testcases'])
            
            return jsonify(list(set(all_testcases)))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Get author metrics
    @app.route('/api/author/<author>/metrics')
    def get_author_metrics(author):
        try:
            testcase = request.args.get('testcase', None)
            
            match_criteria = {'author': author}
            if testcase:
                match_criteria['testcases'] = testcase
            
            collection = get_collection()
            pipeline = [
                {'$match': match_criteria},
                {'$group': {
                    '_id': None,
                    'code_complexity': {'$avg': {'$ifNull': ['$metrics.code_complexity', 0]}},
                    'code_quality': {'$avg': {'$ifNull': ['$metrics.code_quality', 0]}},
                    'code_readability': {'$avg': {'$ifNull': ['$metrics.code_readability', 0]}},
                    'developer_performance': {'$avg': {'$ifNull': ['$metrics.developer_performance', 0]}},
                    'function_complexity': {'$avg': {'$ifNull': ['$metrics.function_complexity', 0]}},
                    'last_commit_date': {'$max': '$last_commit_date'}
                }}
            ]
            
            result = list(collection.aggregate(pipeline))
            
            if not result:
                return jsonify({"error": "No metrics found"}), 404
            
            metrics = result[0]
            del metrics['_id']
            
            # Calculate days since last commit
            if metrics.get('last_commit_date'):
                try:
                    last_commit = datetime.fromisoformat(metrics['last_commit_date'].replace('Z', '+00:00'))
                    current_date = datetime.now()
                    metrics['days_since_last_commit'] = (current_date - last_commit).days
                    metrics['current_date'] = current_date.isoformat()
                except:
                    metrics['days_since_last_commit'] = 0
                    metrics['current_date'] = datetime.now().isoformat()
            
            return jsonify(metrics)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Get author work metrics
    @app.route('/api/author/<author>/work-metrics')
    def get_author_work_metrics(author):
        try:
            collection = get_collection()
            pipeline = [
                {'$match': {'author': author}},
                {'$project': {
                    'testcases': 1,
                    'metrics.total_working_hours': {'$ifNull': ['$metrics.total_working_hours', 0]},
                    'metrics.estimated_time': {'$ifNull': ['$metrics.estimated_time', 0]}
                }}
            ]
            
            result = list(collection.aggregate(pipeline))
            
            if not result:
                return jsonify({"error": "No work metrics found"}), 404
            
            testcase_metrics = {}
            totals = {"total_working_hours": 0, "estimated_time": 0}
            
            for item in result:
                metrics = item.get('metrics', {})
                working_hours = metrics.get('total_working_hours', 0)
                estimated_time = metrics.get('estimated_time', 0)
                
                totals["total_working_hours"] += working_hours
                totals["estimated_time"] += estimated_time
                
                testcases = item.get('testcases', [])
                for testcase in testcases:
                    if testcase not in testcase_metrics:
                        testcase_metrics[testcase] = {
                            "total_working_hours": working_hours,
                            "estimated_time": estimated_time
                        }
                    else:
                        testcase_metrics[testcase]["total_working_hours"] += working_hours
                        testcase_metrics[testcase]["estimated_time"] += estimated_time
            
            formatted_testcases = [{"testcase": tc, **metrics} for tc, metrics in testcase_metrics.items()]
            
            return jsonify({
                "testcases": formatted_testcases,
                "totals": totals
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Get project members time metrics
    @app.route('/api/project/<int:project_id>/members-time-metrics')
    def get_project_members_time_metrics(project_id):
        try:
            collection = get_collection()
            
            # Get all authors for this project
            authors_pipeline = [
                {'$match': {'project_id': project_id}},
                {'$group': {'_id': '$author'}}
            ]
            
            authors = list(collection.aggregate(authors_pipeline))
            author_list = [author['_id'] for author in authors if author['_id']]
            
            results = {}
            for author in author_list:
                pipeline = [
                    {'$match': {'author': author, 'project_id': project_id}},
                    {'$group': {
                        '_id': '$author',
                        'total_working_hours': {'$sum': {'$ifNull': ['$metrics.total_working_hours', 0]}},
                        'estimated_time': {'$sum': {'$ifNull': ['$metrics.estimated_time', 0]}}
                    }}
                ]
                
                author_metrics = list(collection.aggregate(pipeline))
                
                if author_metrics:
                    metrics = author_metrics[0]
                    working_hours = metrics.get('total_working_hours', 0)
                    estimated_time = metrics.get('estimated_time', 0)
                    
                    results[author] = {
                        'total_working_hours': working_hours,
                        'estimated_time': estimated_time,
                        'efficiency_ratio': estimated_time / working_hours if working_hours > 0 else 0
                    }
            
            # Format as array and sort by working hours
            formatted_results = [{"author": author, **metrics} for author, metrics in results.items()]
            formatted_results.sort(key=lambda x: x['total_working_hours'], reverse=True)
            
            return jsonify(formatted_results)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Get project performance scores
    @app.route('/api/project/<int:project_id>/performance-scores')
    def get_project_performance_scores(project_id):
        try:
            collection = get_collection()
            pipeline = [
                {'$match': {'project_id': project_id}},
                {'$group': {
                    '_id': '$author',
                    'total_working_hours': {'$sum': {'$ifNull': ['$metrics.total_working_hours', 0]}},
                    'estimated_time': {'$sum': {'$ifNull': ['$metrics.estimated_time', 0]}},
                    'avg_code_quality': {'$avg': {'$ifNull': ['$metrics.code_quality', 0]}},
                    'avg_code_readability': {'$avg': {'$ifNull': ['$metrics.code_readability', 0]}},
                    'avg_function_complexity': {'$avg': {'$ifNull': ['$metrics.function_complexity', 0]}},
                    'avg_code_complexity': {'$avg': {'$ifNull': ['$metrics.code_complexity', 0]}},
                    'avg_developer_performance': {'$avg': {'$ifNull': ['$metrics.developer_performance', 0]}},
                    'document_count': {'$sum': 1}
                }},
                {'$project': {
                    'author': '$_id',
                    'total_working_hours': 1,
                    'estimated_time': 1,
                    'avg_code_quality': 1,
                    'avg_code_readability': 1,
                    'avg_function_complexity': 1,
                    'avg_code_complexity': 1,
                    'avg_developer_performance': 1,
                    'document_count': 1,
                    '_id': 0
                }}
            ]
            
            results = list(collection.aggregate(pipeline))
            
            performance_data = []
            for result in results:
                author = result['author']
                
                # Get values with defaults
                total_working_hours = max(result.get('total_working_hours', 1), 1)
                estimated_time = max(result.get('estimated_time', 1), 1)
                code_quality = result.get('avg_code_quality', 0)
                code_readability = result.get('avg_code_readability', 0)
                function_complexity = result.get('avg_function_complexity', 0)
                code_complexity = result.get('avg_code_complexity', 0)
                
                # Calculate performance score
                try:
                    time_ratio = estimated_time / total_working_hours
                    quality_factor = (0.7 * code_quality) + (0.3 * code_readability)
                    complexity_factor = (1 + 0.6 * function_complexity) + (0.4 * code_complexity)
                    
                    # Ensure positive values
                    time_ratio = max(time_ratio, 0.01)
                    quality_factor = max(quality_factor, 0.01)
                    complexity_factor = max(complexity_factor, 1)
                    
                    performance_score = (time_ratio * quality_factor) * complexity_factor
                    performance_score = min(max(performance_score, 0.001), 1000)  # Cap values
                    
                except:
                    performance_score = 0
                
                performance_data.append({
                    'author': author,
                    'performance_score': round(performance_score, 3),
                    'total_working_hours': total_working_hours,
                    'estimated_time': estimated_time,
                    'time_efficiency': round(estimated_time / total_working_hours, 3) if total_working_hours > 0 else 0,
                    'avg_code_quality': round(code_quality, 2),
                    'avg_code_readability': round(code_readability, 2),
                    'avg_function_complexity': round(function_complexity, 2),
                    'avg_code_complexity': round(code_complexity, 2),
                    'document_count': result.get('document_count', 0)
                })
            
            # Sort by performance score
            performance_data.sort(key=lambda x: x['performance_score'], reverse=True)
            
            return jsonify(performance_data)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500