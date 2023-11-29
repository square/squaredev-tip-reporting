import { Loader, Modal } from '@mantine/core';
import { StatsGridIcons } from './stats-grid';
import DetailsTable from './details-table';

export const prettyMoney = (value: number) => {
  return (value / 100).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  })
}

const CustomModal = ({opened, close, selectedDetails, isLoading}: {opened: any, close: any, selectedDetails: any, isLoading: boolean}) => {
  let [orderTotal, tipTotal] = [0, 0]
  selectedDetails.orders?.forEach((order:any) => {
    orderTotal += order?.totalMoney?.amount - order?.totalTip?.amount
    tipTotal += order?.totalTip?.amount
  })
  return (
    <>
      <Modal opened={opened} onClose={close} title="Shift Details" size="xl">
        <h1>{selectedDetails.selected_team_member_name}</h1>
        {isLoading ?
        <div style={{display: "flex", justifyContent: "center", alignItems: "center"}}>
          <Loader/>
        </div>
          :
          <>
          <StatsGridIcons data={[{
                title: "Order Revenue",
                value: prettyMoney(orderTotal),
                diff: 1,
            },
            {
                title: "Tip Revenue",
                value: prettyMoney(tipTotal),
                diff: 1,
            },
            {
                title: "Average Tip",
                value: prettyMoney(tipTotal / selectedDetails?.orders?.length),
                diff: -1,
            }
            ]}/>
            <DetailsTable orders={selectedDetails.orders}/>
          </>
        }
      </Modal>
    </>
  );
}

export default CustomModal