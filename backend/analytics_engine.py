import matplotlib
matplotlib.use('Agg') # Set backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import io
import base64
from psycopg2.extras import RealDictCursor
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta

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

    def get_progress_report(self, time_filter='7d'):
        """
        Returns data for the 'Score vs Time' graph with filtering.
        """
        raw_data = self.fetch_raw_data()
        
        # Filter Logic
        now = datetime.now()
        filtered_data = []

        # Determine start date based on filter
        start_date = None
        
        if time_filter == '7d':
            start_date = now - timedelta(days=7)
        elif time_filter == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == 'this_month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == 'prev_month':
            # specialized logic for range (start of prev month to end of prev month)
            first_day_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = first_day_this_month
            start_date = (end_date - timedelta(days=1)).replace(day=1)
            
            # Filter specifically for this range
            for row in raw_data:
                if start_date <= row['attempted_at'] < end_date:
                    filtered_data.append(row)
            # Skip the standard loop below
            raw_data = [] # Clear to skip standard loop
        elif time_filter == 'this_year':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_filter == 'lifetime':
            start_date = None # No filter
        
        # Standard filtering (Start Date -> Now)
        if time_filter != 'prev_month':
            for row in raw_data:
                if start_date:
                    if row['attempted_at'] >= start_date:
                        filtered_data.append(row)
                else:
                    filtered_data.append(row)

        dates = [] 
        scores = []
        
        for row in filtered_data:
            dates.append(row['attempted_at'])
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
        
        # --- Chart 1: Topic Accuracy (Scrollable Version) ---
        topic_stats = self.process_topic_performance()
        if topic_stats:
            # Reverse for Top-to-Bottom display
            topic_stats_rev = list(reversed(topic_stats))
            topics = [t['topic'] for t in topic_stats_rev]
            accuracies = [t['accuracy'] for t in topic_stats_rev]
            
            colors = []
            for acc in accuracies:
                if acc >= 80: colors.append('#4ade80')      # Green
                elif acc >= 50: colors.append('#facc15')    # Yellow
                else: colors.append('#fca5a5')              # Pink/Red

            # DYNAMIC HEIGHT: 0.8 inches per topic for thick, readable bars
            fig_height = max(6, len(topics) * 0.8)
            plt.figure(figsize=(10, fig_height))
            
            # Thick bars (height=0.6)
            bars = plt.barh(topics, accuracies, color=colors, alpha=0.9, height=0.6)
            
            plt.grid(axis='x', linestyle='--', alpha=0.4)
            plt.xlim(0, 115) 
            plt.title('Accuracy per Topic', fontsize=16, fontweight='bold', pad=20, color='#1e293b')
            plt.xlabel('Accuracy (%)', fontsize=14, labelpad=10, color='#475569')
            
            ax = plt.gca()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1')
            ax.spines['bottom'].set_color('#cbd5e1')
            ax.tick_params(colors='#475569', labelsize=12)
            
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 2, bar.get_y() + bar.get_height()/2.,
                        f'{width}%',
                        ha='left', va='center', fontsize=11, fontweight='bold', color='#1e293b')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
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

        # --- Chart 2: Score Progression (Professional Time-Series) ---
        # Defaults to 7d to match UI
        charts['progress_chart'] = self.generate_progress_chart_img('7d')

        # --- Chart 3: Radar Chart (Skill Distribution) ---
        charts['radar_chart'] = self.generate_radar_chart()
        
        return charts

    def generate_radar_chart(self):
        """
        Generates a Radar Chart (Spider Plot) for topic performance.
        """
        import numpy as np
        
        topic_stats = self.process_topic_performance()
        if not topic_stats:
            return None

        # Take top 6 topics to maintain a balanced radar shape
        stats_to_plot = topic_stats[:6]
        
        labels = [t['topic'] for t in stats_to_plot]
        values = [t['accuracy'] for t in stats_to_plot]
        
        # Number of variables
        num_vars = len(labels)
        if num_vars < 3:
            return None # Radar chart needs at least 3 variables to look good

        # Split the circle into even parts and save the angles
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        # The plot is a circle, so we need to "close the loop" for the lines
        values += values[:1]
        angles += angles[:1]
        # FIX: Do NOT append to the labels list here! Keep labels at original length.

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        
        # Draw one axe per variable + add labels (angles[:-1] matches the unappended labels list)
        plt.xticks(angles[:-1], labels, color='#1e293b', size=10)
        
        # Draw ylabels
        ax.set_rlabel_position(0)
        plt.yticks([25, 50, 75, 100], ["25", "50", "75", "100"], color="#94a3b8", size=8)
        plt.ylim(0, 100)
        
        # Plot data
        ax.plot(angles, values, linewidth=2, linestyle='solid', color='#db2777')
        
        # Fill area
        ax.fill(angles, values, '#db2777', alpha=0.25)
        
        # Style
        ax.spines['polar'].set_color('#e2e8f0')
        ax.set_facecolor('#fafafa')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, transparent=True)
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
        return img_str

    def generate_progress_chart_img(self, time_filter='7d'):
        """
        Generates just the progress chart based on the filter.
        Returns base64 string.
        """
        progress = self.get_progress_report(time_filter)
        
        if progress and len(progress['data']) > 0:
            dates = progress['labels']
            scores = progress['data']
            
            plt.figure(figsize=(10, 6))
            
            # 1. Plot the "Passing Grade" Threshold (70%)
            plt.axhline(y=70, color='#10b981', linestyle='--', linewidth=1.5, alpha=0.5, label='Passing (70%)')
            
            # 2. Plot Individual Attempts (Scatter)
            plt.scatter(dates, scores, color='#db2777', s=60, zorder=3, edgecolors='white', linewidth=2, label='Quiz Attempt')
            
            # 3. Plot Trend Line (Connect the dots)
            # Since we use precise time, this line will flow naturally from left to right
            plt.plot(dates, scores, color='#db2777', linewidth=2, alpha=0.4, linestyle='-')
            
            # 4. Fill Area Under Line
            plt.fill_between(dates, scores, color='#db2777', alpha=0.05)
            
            # Styling
            plt.ylim(0, 105)
            plt.grid(axis='y', linestyle='--', alpha=0.3)
            plt.title('Score Progression History', fontsize=14, fontweight='bold', pad=20, color='#1e293b')
            
            # X-Axis Date Formatting (Smart Scaling)
            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            # Calculate appropriate interval for ticks based on data range if needed, but auto usually works
            plt.xticks(rotation=0)
            
            # Remove clutter
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1')
            ax.spines['bottom'].set_color('#cbd5e1')
            ax.tick_params(colors='#475569')
            
            # Add Legend
            plt.legend(frameon=False, loc='lower right', fontsize=9)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            return img_str
        else:
            # Empty state
            plt.figure(figsize=(6, 4))
            plt.text(0.5, 0.5, 'No Quiz Data Yet', ha='center', va='center', fontsize=14, color='#94a3b8')
            plt.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            return img_str

class GlobalAnalyticsEngine:
    def __init__(self, db_connection):
        self.conn = db_connection

    def fetch_raw_global_data(self):
        """Fetches raw attempt data for Python processing."""
        from psycopg2.extras import RealDictCursor
        query = """
            SELECT a.percentage, a.attempted_at, s.subject_name
            FROM attempts a
            JOIN topics t ON a.topic_id = t.topic_id
            JOIN subjects s ON t.subject_id = s.subject_id
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()

    def process_subject_averages(self, raw_data):
        """DSA: Uses a Hash Map to aggregate scores by subject."""
        subj_map = {}
        for row in raw_data:
            subj = row['subject_name']
            if subj not in subj_map:
                subj_map[subj] = []
            subj_map[subj].append(row['percentage'])
            
        stats = []
        for subj, scores in subj_map.items():
            stats.append({
                "subject": subj,
                "avg": sum(scores) / len(scores)
            })
            
        # DSA: Sort descending by average
        return sorted(stats, key=lambda x: x['avg'], reverse=True)

    def process_daily_activity(self, raw_data):
        """DSA: Uses a Hash Map to count quizzes taken per day."""
        from datetime import datetime
        activity_map = {}
        
        for row in raw_data:
            # Ensure we have a date object
            dt = row['attempted_at']
            date_val = dt.date() if isinstance(dt, datetime) else dt
            
            if date_val not in activity_map:
                activity_map[date_val] = 0
            activity_map[date_val] += 1
            
        # Sort chronologically
        sorted_activity = sorted(activity_map.items(), key=lambda x: x[0])
        
        # Return only the last 14 active days
        return sorted_activity[-14:]

    def generate_global_charts(self):
        """Generates Matplotlib charts from the Python-processed data."""
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import io
        import base64

        charts = {}
        raw_data = self.fetch_raw_global_data()
        if not raw_data:
            return charts

        # --- Chart 1: Average Score by Subject (Scrollable Horizontal Bar Chart) ---
        subj_stats = self.process_subject_averages(raw_data)
        if subj_stats:
            # Reverse list so the highest score is at the top of the chart
            subj_stats_rev = list(reversed(subj_stats))
            subjects = [t['subject'] for t in subj_stats_rev]
            scores = [t['avg'] for t in subj_stats_rev]

            # Dynamic Height: Scales with the number of subjects to prevent squishing
            fig_height = max(5, len(subjects) * 0.6)
            plt.figure(figsize=(10, fig_height))
            
            # Create horizontal bars
            bars = plt.barh(subjects, scores, color='#8b5cf6', alpha=0.85, height=0.6, edgecolor='white', linewidth=2)
            
            plt.xlim(0, 115) # Give extra room on the right for text labels
            
            # Center title on the figure (not just the axes)
            plt.suptitle('Average Score by Subject', fontsize=14, fontweight='bold', color='#1e293b', y=0.92)
            
            plt.xlabel('Average Score (%)', fontsize=12, color='#475569', labelpad=8) # Reduced font
            plt.subplots_adjust(top=0.85) # Reserve space for suptitle
            
            ax = plt.gca()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1')
            ax.spines['bottom'].set_color('#cbd5e1')
            ax.tick_params(colors='#475569', labelsize=10) # Reduced subject name font size
            plt.grid(axis='x', linestyle='--', alpha=0.3)
            
            # Add value labels at the end of each bar
            for bar in bars:
                width = bar.get_width()
                plt.text(width + 2, bar.get_y() + bar.get_height()/2.,
                        f'{width:.1f}%',
                        ha='left', va='center', fontsize=11, fontweight='bold', color='#1e293b')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            charts['subject_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()

        # --- Chart 2: Platform Activity (Line Chart) ---
        activity_stats = self.process_daily_activity(raw_data)
        if activity_stats:
            dates = [item[0] for item in activity_stats]
            counts = [item[1] for item in activity_stats]

            plt.figure(figsize=(8, 4.5))
            plt.plot(dates, counts, marker='o', color='#db2777', linewidth=2.5, markersize=8, markeredgecolor='white', markeredgewidth=2)
            plt.fill_between(dates, counts, color='#db2777', alpha=0.1)
            
            plt.title('Platform Activity (Quizzes Taken)', fontsize=14, fontweight='bold', color='#1e293b', pad=15)
            plt.ylabel('Quizzes Taken', color='#475569')
            
            ax = plt.gca()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1')
            ax.spines['bottom'].set_color('#cbd5e1')
            ax.tick_params(colors='#475569')
            plt.xticks(rotation=45)
            plt.grid(axis='y', linestyle='--', alpha=0.3)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            charts['activity_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()

        return charts
