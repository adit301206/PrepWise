import matplotlib
matplotlib.use('Agg') # Set backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
from psycopg2.extras import RealDictCursor

class AnalyticsEngine:
    def __init__(self, user_id, db_connection):
        """
        OOP: Encapsulates analytics logic for a specific user.
        DSA: Will use Hash Maps and Sorting algorithms for data processing.
        """
        self.user_id = user_id
        self.conn = db_connection

    def fetch_raw_data(self):
        """
        Fetches detailed attempt history joining relevant tables.
        Returns a list of dictionaries (rows).
        """
        query = """
            SELECT 
                a.attempt_id,
                a.score,
                a.total_questions,
                a.percentage,
                a.attempted_at,
                t.topic_name,
                s.subject_name
            FROM attempts a
            JOIN topics t ON a.topic_id = t.topic_id
            JOIN subjects s ON t.subject_id = s.subject_id
            WHERE a.user_id = %s
            ORDER BY a.attempted_at ASC;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (self.user_id,))
            return cur.fetchall()

    def get_subject_performance(self):
        """
        Calculates average score per Subject.
        SQL: Joins attempts -> topics -> subjects and groups by subject_name.
        """
        query = """
            SELECT s.subject_name, AVG(a.score) as avg_score, COUNT(a.attempt_id) as attempts
            FROM attempts a
            JOIN topics t ON a.topic_id = t.topic_id
            JOIN subjects s ON t.subject_id = s.subject_id
            WHERE a.user_id = %s
            GROUP BY s.subject_name
            ORDER BY avg_score DESC
            LIMIT 5;
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (self.user_id,))
            results = cur.fetchall()
            
            # Format results for template
            formatted = []
            for row in results:
                formatted.append({
                    "subject": row['subject_name'],
                    "accuracy": round(row['avg_score'], 1) if row['avg_score'] else 0,
                    "attempts": row['attempts']
                })
            return formatted

    def process_topic_performance(self):
        """
        DSA: Uses a Hash Map (Dictionary) to aggregate scores by topic.
        Returns a sorted list of topic stats from Highest to Lowest accuracy.
        """
        raw_data = self.fetch_raw_data()
        
        # DSA: Hash Map for O(n) aggregation
        # Key: topic_name, Value: list of percentages
        topic_map = {}
        
        for row in raw_data:
            topic = row['topic_name']
            percentage = row['percentage']
            
            if topic not in topic_map:
                topic_map[topic] = []
            topic_map[topic].append(percentage)
            
        # Calculate Averages
        stats = []
        for topic, scores in topic_map.items():
            avg_score = sum(scores) / len(scores)
            stats.append({
                "topic": topic,
                "accuracy": round(avg_score, 1),
                "attempts": len(scores)
            })
            
        # DSA: Sorting Algorithm (Timsort via sorted)
        # Sort by accuracy (Descending)
        sorted_stats = sorted(stats, key=lambda x: x['accuracy'], reverse=True)
        
        return sorted_stats

    def get_weakest_areas(self):
        """
        Returns the bottom 3 topics based on accuracy.
        """
        # We assume process_topic_performance returns sorted High -> Low
        stats = self.process_topic_performance()
        
        # If stats is empty, return empty
        if not stats:
            return []
            
        # Get last 3 elements (Weakest)
        # Since it's High -> Low, the end of the list is the weakest.
        # We want to return them.
        weakest = stats[-3:] 
        
        # Reverse to show Lowest first in the return list if desired, 
        # or just return as is (Low to High relative to each other? No, they are Low abs).
        # List slice [-3:] gives [3rd lowest, 2nd lowest, Lowest]
        # Let's sort them explicitly by accuracy Ascending for the "Weakest" display
        return sorted(weakest, key=lambda x: x['accuracy'])

    def get_strongest_areas(self):
        """
        Returns top 3 topics.
        """
        stats = self.process_topic_performance()
        return stats[:3]

    def get_progress_report(self):
        """
        Returns data for the 'Score vs Time' graph.
        """
        raw_data = self.fetch_raw_data()
        
        # Prepare arrays for Chart.js
        dates = []
        scores = []
        
        for row in raw_data:
            # Format date as 'Jan 01'
            date_str = row['attempted_at'].strftime("%b %d")
            dates.append(date_str)
            scores.append(row['percentage'])
            
        return {
            "labels": dates,
            "data": scores
        }

    def get_overall_stats(self):
        """
        Calculates aggregate stats for the top cards.
        """
        raw_data = self.fetch_raw_data()
        if not raw_data:
            return {
                "accuracy": 0,
                "total_quizzes": 0,
                "streak": 0,
                "trend": 0
            }
            
        total_quizzes = len(raw_data)
        avg_accuracy = sum(r['percentage'] for r in raw_data) / total_quizzes
        
        # Calculate Streak (consecutive quizzes >= 70%)
        streak = 0
        for row in reversed(raw_data): # Start from most recent
            if row['percentage'] >= 70:
                streak += 1
            else:
                break
                
        # Calculate Trend (Last 5 vs Previous 5? Or simple Last vs Avg?)
        # Let's do: Last Quiz vs Average of Previous
        trend = 0
        if len(raw_data) > 1:
            last = raw_data[-1]['percentage']
            previous_avg = sum(r['percentage'] for r in raw_data[:-1]) / (len(raw_data) - 1)
            diff = last - previous_avg
            trend = round(diff, 1)
            
        return {
            "accuracy": round(avg_accuracy, 1),
            "total_quizzes": total_quizzes,
            "streak": streak,
            "trend": trend
        }

    def generate_charts(self):
        """
        Generates analysis charts using Matplotlib and returns them as Base64 strings.
        """
        charts = {}
        
        # --- Chart 1: Topic Accuracy (Bar Chart) ---
        topic_stats = self.process_topic_performance()
        if topic_stats:
            topics = [t['topic'] for t in topic_stats]
            accuracies = [t['accuracy'] for t in topic_stats]
            
            plt.figure(figsize=(10, 6))
            # Use requested color #6366f1
            bars = plt.bar(topics, accuracies, color='#6366f1', alpha=0.8, width=0.6)
            
            # Styling
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            plt.ylim(0, 105)
            plt.title('Accuracy per Topic', fontsize=14, fontweight='bold', pad=20, color='#1e293b')
            plt.xlabel('Topics', fontsize=12, labelpad=10, color='#475569')
            plt.ylabel('Accuracy (%)', fontsize=12, labelpad=10, color='#475569')
            
            # Remove spines
            ax = plt.gca()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1')
            ax.spines['bottom'].set_color('#cbd5e1')
            ax.tick_params(colors='#475569')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height}%',
                        ha='center', va='bottom', fontsize=10, color='#1e293b')
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150) # High DPI for crispness
            buf.seek(0)
            charts['topic_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
        else:
            # Generate empty placeholder or handle in template? 
            # Let's generate a clear "No Data" image to prevent broken image icons
            plt.figure(figsize=(6, 4))
            plt.text(0.5, 0.5, 'No Data Available', 
                     ha='center', va='center', fontsize=14, color='#94a3b8')
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            charts['topic_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()

        # --- Chart 2: Progress Over Time (Line Chart) ---
        progress = self.get_progress_report()
        # progress returns { "labels": [...], "data": [...] }
        if progress and len(progress['data']) > 0:
            dates = progress['labels']
            scores = progress['data']
            
            plt.figure(figsize=(10, 6))
            # Plot line
            plt.plot(dates, scores, marker='o', color='#db2777', linewidth=3, 
                     markersize=8, markerfacecolor='white', markeredgewidth=3)
            
            # Styling
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            plt.ylim(0, 105)
            plt.fill_between(dates, scores, color='#db2777', alpha=0.1) # Area fill
            
            plt.title('Score Progression', fontsize=14, fontweight='bold', pad=20, color='#1e293b')
            plt.xlabel('Date', fontsize=12, labelpad=10, color='#475569')
            plt.ylabel('Score (%)', fontsize=12, labelpad=10, color='#475569')
            
            ax = plt.gca()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1')
            ax.spines['bottom'].set_color('#cbd5e1')
            ax.tick_params(colors='#475569')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            charts['progress_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
        else:
            # Empty placeholder
            plt.figure(figsize=(6, 4))
            plt.text(0.5, 0.5, 'No Quiz Data Yet', 
                     ha='center', va='center', fontsize=14, color='#94a3b8')
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            charts['progress_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()

        return charts
