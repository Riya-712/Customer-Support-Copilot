import streamlit as st
from src.evaluation.evaluator import Evaluator
st.set_page_config(page_title='Evaluation',layout='wide')
st.title('Held-out Evaluation')
st.caption('The 20 evaluation tickets are excluded from the support_tickets Chroma collection.')
if st.button('Run held-out evaluation',type='primary'):
    with st.spinner('Running evaluation — this makes LLM calls and may take a while…'):
        try: st.session_state['eval']=Evaluator().run()
        except Exception as e: st.error(str(e)); st.stop()
res=st.session_state.get('eval')
if res:
    c1,c2,c3=st.columns(3); c1.metric('Tickets',res['n']); c2.metric('Intent accuracy',f"{res['intent_accuracy']:.1%}"); c3.metric('Intent macro F1',f"{res['intent_macro_f1']:.1%}")
    rows=[x for x in res['results'] if 'true_intent' in x]
    if rows:
        retrieval_recall=sum(bool(x['kb_ids']) for x in rows)/len(rows)
        grounding=sum(x['grounded'] for x in rows)/len(rows)
        citation=sum(x['citation_correct'] for x in rows)/len(rows)
        action=sum(x['recommended_action']==x['ground_truth_action'] for x in rows)/len(rows)
        a,b,c,d,e=st.columns(5); a.metric('Recall@5',f"{res['retrieval_recall_at_5']:.1%}"); b.metric('Precision@5',f"{res['retrieval_precision_at_5']:.1%}"); c.metric('MRR',f"{res['retrieval_mrr']:.3f}"); d.metric('Groundedness',f"{res['groundedness_rate']:.1%}"); e.metric('Citation correctness',f"{res['citation_correctness']:.1%}")
        st.metric('Recommendation agreement',f"{res['recommendation_agreement']:.1%}")
        st.dataframe(rows,use_container_width=True)
else: st.info('Run the evaluation to populate metrics.')
