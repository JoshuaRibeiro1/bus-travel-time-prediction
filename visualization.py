"""Components extracted from the original bus travel-time baseline notebook."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def create_charts(metrics, by_route, by_month, out):
    fig, axes = plt.subplots(1,2,figsize=(12,4))
    metrics.set_index('model').MAE_minutes.plot.barh(ax=axes[0],color=['#888888','#bbbbbb','#527d9c','#264d34'])
    axes[0].set_xlabel('Mean absolute error (minutes)'); axes[0].set_title('Held-out prediction error')
    by_route.pivot(index='group',columns='model',values='MAE_minutes')[names].plot.bar(ax=axes[1])
    axes[1].set_ylabel('MAE (minutes)'); axes[1].set_xlabel('Route'); axes[1].set_title('Errors by route')
    axes[1].legend(fontsize=8)
    axes[1].set_ylim(0,1.15)
    fig.tight_layout(); fig.savefig(out/'baseline_comparison.png',dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9,4))
    by_month.pivot(index='group',columns='model',values='MAE_minutes')[names].plot(marker='o',ax=ax)
    ax.set_ylabel('MAE (minutes)'); ax.set_xlabel('Test month'); ax.set_title('Performance over held-out months')
    fig.tight_layout(); fig.savefig(out/'monthly_errors.png',dpi=160); plt.close(fig)
    return None

