import argparse
from src.data.ticket_repository import TicketRepository
from src.support.ticket_analyzer import TicketAnalyzer

def main():
    parser=argparse.ArgumentParser(description='NovaMart Support Copilot')
    parser.add_argument('--ticket-id',required=True)
    args=parser.parse_args()
    ticket=TicketRepository().get_ticket(args.ticket_id)
    if not ticket: raise SystemExit(f'Ticket not found: {args.ticket_id}')
    clean=TicketRepository.for_inference(ticket)
    result=TicketAnalyzer().analyze(clean)
    print(result.response.model_dump_json(indent=2))
if __name__=='__main__': main()
