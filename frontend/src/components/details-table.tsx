import { Table } from '@mantine/core';
import { prettyMoney } from './modal';



function DetailsTable({orders}: any) {
  const rows = orders?.map((order: any) => {
    const orderAmount = order?.totalMoney?.amount - order?.totalTip?.amount
    const tipAmount = order?.totalTip?.amount
    const tipPercentage = Math.round(((order?.totalTip?.amount / order?.totalMoney?.amount) * 100) *10) / 10

    return (
    <tr key={order?.id}>
      <td>{order?.ticketName}</td>
      <td>{`${order?.customer?.givenName} ${order?.customer?.familyName}`}</td>
      <td>{prettyMoney(orderAmount)}</td>
        <td>{prettyMoney(tipAmount)}</td>
        <td>{`${tipPercentage}%`}</td>
    </tr>
  )});
  return (
    <Table>
      <thead>
        <tr>
          <th>Ticket Name</th>
          <th>Customer</th>
          <th>Order Total</th>
          <th>Tip Amount</th>
          <th>Tip Percent</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </Table>
  );
}

export default DetailsTable